# -*- coding: utf-8 -*-
import io
import csv
import time
import unittest
try:
    from unittest.mock import patch, MagicMock
    from unittest import mock
except:
    import mock
    from mock import patch, MagicMock

# Import the package under test
from cnmc_client.client import Client, CUPS_CHUNK_SIZE
from cnmc_client.models import CNMC_ListEntry

# -----------------
# Helpers / Doubles
# -----------------

class DummyAPI:
    """A minimal drop-in for CNMC_API used only for tests.
    It records calls and returns canned responses shaped like the real API."""
    def __init__(self):
        self.calls = []
        self.NIF = "B12345678"  # what client.list expects to send

    def get(self, resource, **kwargs):
        self.calls.append(("GET", resource, kwargs))
        # EchoSeguro (test endpoint)
        if resource == "/test/v1/echoseguro":
            message = kwargs.get("params", {}).get("m", "")
            return {
                "code": 200,
                "error": False,
                "result": {"mensaje": message}
            }
        # Download file by name
        if resource.startswith("/ficheros/v1/descarga/"):
            filename = resource.split("/")[-1]
            return {
                "code": 200,
                "error": False,
                "result": {"nombre": filename, "ok": True}
            }
        raise AssertionError("Unhandled GET resource: {resource}".format(resource=resource))

    def post(self, resource, **kwargs):
        self.calls.append(("POST", resource, kwargs))
        if resource == "/ficheros/v1/consultar":
            params = kwargs.get("params", {})
            # Return two dummy entries shaped like the docs/models
            entries = [
                {
                    "uuid": "111",
                    "idProcedimiento": 2,
                    "nifEmpresa": params.get("nifEmpresa"),
                    "numeroBytes": 12,
                    "tipoFichero": "SGDA",
                    "estado": params.get("estado", "DISPONIBLE"),
                    "mime": "text/csv",
                    "nombre": "file1.csv",
                    "hash": "abc",
                    "fechaDisponibilidad": "2020-01-01T00:00:00Z",
                    "fechaCaducidad": "2020-02-01T00:00:00Z",
                    "uriDescargas": "/ficheros/v1/descarga/file1.csv",
                    "descripción": "fichero 1"
                },
                {
                    "uuid": "222",
                    "idProcedimiento": 2,
                    "nifEmpresa": params.get("nifEmpresa"),
                    "numeroBytes": 34,
                    "tipoFichero": "SGDA",
                    "estado": params.get("estado", "DISPONIBLE"),
                    "mime": "text/csv",
                    "nombre": "file2.csv",
                    "hash": "def",
                    "fechaDisponibilidad": "2020-01-02T00:00:00Z",
                    "fechaCaducidad": "2020-02-02T00:00:00Z",
                    "uriDescargas": "/ficheros/v1/descarga/file2.csv",
                    "descripción": "fichero 2"
                },
            ]
            return {"code": 200, "error": False, "result": entries}
        raise AssertionError("Unhandled POST resource: {resource}".format(resource=resource))

    def download(self, resource, **kwargs):
        self.calls.append(("DOWNLOAD", resource, kwargs))
        # Return a tiny CSV payload
        payload = b"col1,col2\nA,1\nB,2\n"
        return {"code": 200, "error": False, "result": io.BytesIO(payload)}


class ClientTestCase(unittest.TestCase):
    def setUp(self):
        # Create a real Client but swap the API for our dummy
        self.client = Client(key="k", secret="s")
        self.client.API = DummyAPI()

    # --------
    # .test()
    # --------
    def test_test_endpoint_echoes_message(self):
        res = self.client.test("hola mundo")
        self.assertEqual(res.result.mensaje, "hola mundo")
        self.assertIn(("GET", "/test/v1/echoseguro", mock.ANY), self.client.API.calls)

    # --------
    # .list()
    # --------
    def test_list_default_filters_and_shape(self):
        # Call without filters -> defaults to estado="DISPONIBLE"
        lst = self.client.list()
        # result is a list-like inside a Munch; ensure two entries
        self.assertEqual(len(lst.result), 2)
        self.assertTrue(all(isinstance(e, CNMC_ListEntry) for e in lst.result))

        # Ensure the API received expected params
        _, _, kwargs = self.client.API.calls[-1]
        params = kwargs.get("params", {})
        self.assertEqual(params["estado"], "DISPONIBLE")
        self.assertEqual(params["nifEmpresa"], self.client.API.NIF)
        self.assertEqual(params["idProcedimiento"], "2")

    def test_list_with_date_filters(self):
        lst = self.client.list(date_start="2020-01-01", date_end="2020-01-31")
        _, _, kwargs = self.client.API.calls[-1]
        params = kwargs.get("params", {})
        self.assertEqual(params["fechaDesde"], "2020-01-01")
        # NOTE: current code sets 'fechaHasta' from date_start (probable bug); document behavior
        self.assertEqual(params["fechaHasta"], "2020-01-01")
        self.assertEqual(len(lst.result), 2)

    # --------
    # .fetch()
    # --------
    def test_fetch_as_csv_reader(self):
        cups = ["ES00TEST{0:02d}".format(i) for i in range(3)]
        file = self.client.fetch(cups, "SIPS2_PS_ELECTRICIDAD", as_csv=True)
        # Read the csv rows
        rows = list(file.result)
        self.assertEqual(rows[0]["col1"], "A")
        self.assertEqual(rows[1]["col2"], "2")

        # Ensure params contained the cups list joined by comma
        print("pepe", self.client.API.calls)
        method, resource, kwargs = self.client.API.calls[0]
        self.assertEqual(method, "DOWNLOAD")
        self.assertIn("cups", kwargs["params"])
        self.assertEqual(kwargs["params"]["cups"], ",".join(cups))

    def test_fetch_rejects_oversized_chunks(self):
        cups = ["C{0}".format(i) for i in range(CUPS_CHUNK_SIZE + 1)]
        with self.assertRaises(AssertionError):
            self.client.fetch(cups, "SIPS2_PS_ELECTRICIDAD")

    # -----------------
    # .fetch_massive()
    # -----------------
    def test_fetch_massive_chunks_and_wait(self):
        cups = ["C{0:02d}".format(i) for i in range(CUPS_CHUNK_SIZE * 2 + 1)]  # 21 -> 3 chunks
        with patch.object(self.client, "fetch", return_value="OK") as mock_fetch, \
             patch("time.sleep") as mock_sleep:
            res = self.client.fetch_massive(cups, "SIPS2_PS_ELECTRICIDAD", as_csv=False, wait=0.1)

        self.assertEqual(res, ["OK", "OK", "OK"])
        # 3 chunks -> 3 calls
        self.assertEqual(mock_fetch.call_count, 3)
        # Should sleep twice between the 3 chunks
        self.assertEqual(mock_sleep.call_count, 2)
        mock_sleep.assert_called_with(0.1)

    # ----------
    # .download()
    # ----------
    def test_download_forwards_response(self):
        res = self.client.download("file1.csv")
        self.assertEqual(res["code"], 200)
        self.assertTrue(res["result"]["ok"])
        self.assertEqual(res["result"]["nombre"], "file1.csv")


if __name__ == "__main__":
    unittest.main()