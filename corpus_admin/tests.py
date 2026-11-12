"""Pruebas de regresión para el parseo y validación de cabeceras ``csv``."""

import json
import os
import tempfile
from pathlib import Path

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import SimpleTestCase, override_settings

from .helpers import check_extra_fields, csv_reader, header_normalizer, pdf_uploader


class HeaderNormalizerTests(SimpleTestCase):
    """La cabecera se normaliza y se valida antes de cualquier efecto."""

    def test_normaliza_espacios_y_mayusculas(self):
        self.assertEqual(
            header_normalizer(" l1,l2 , variant "), ["l1", "l2", "variant"]
        )

    def test_rechaza_columna_vacia_por_coma_final(self):
        with self.assertRaisesMessage(ValueError, "nombres de columna vacíos"):
            header_normalizer("l1,l2,")

    def test_rechaza_columna_vacia_en_linea_malformada(self):
        with self.assertRaisesMessage(ValueError, "nombres de columna vacíos"):
            header_normalizer("l1,,l2")

    def test_rechaza_duplicados_despues_de_normalizar(self):
        with self.assertRaisesMessage(ValueError, "columnas duplicadas"):
            header_normalizer("l1, l2 , L1")

    def test_rechaza_faltante_de_l1(self):
        with self.assertRaisesMessage(ValueError, "'l1' y 'l2'"):
            header_normalizer("l2,variant")

    def test_rechaza_faltante_de_l2(self):
        with self.assertRaisesMessage(ValueError, "'l1' y 'l2'"):
            header_normalizer("l1,variant")

    def test_rechaza_cabecera_vacia(self):
        with self.assertRaises(ValueError):
            header_normalizer("")
        with self.assertRaises(ValueError):
            header_normalizer("\n")


class CsvReaderTests(SimpleTestCase):
    """``csv_reader`` aplica la validación de cabecera al leer el archivo."""

    def test_devuelve_cabecera_normalizada_y_datos(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir, "doc.csv")
            csv_path.write_text(
                " l1,l2 , variant \nhola,hi,es\nadios,bye,es\n", encoding="utf-8"
            )
            header, data = csv_reader(csv_path)
        self.assertEqual(header, ["l1", "l2", "variant"])
        self.assertEqual(data, "hola,hi,es\nadios,bye,es")

    def test_rechaza_cabecera_con_columna_vacia(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            csv_path = Path(tmp_dir, "doc.csv")
            csv_path.write_text("l1,l2,\nhola,hi\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                csv_reader(csv_path)


class CheckExtraFieldsTests(SimpleTestCase):
    """La detección de campos extra usa nombres ya normalizados."""

    def setUp(self):
        # ``check_extra_fields`` lee elastic-config.json desde el directorio
        # actual; se fija un fixture para no depender de la config local.
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        config = {
            "mappings": {
                "properties": {
                    "document_id": {"type": "keyword"},
                    "document_name": {"type": "keyword"},
                    "pdf_file": {"type": "keyword"},
                    "l1": {"type": "text"},
                    "l2": {"type": "text"},
                    "variant": {"type": "keyword"},
                }
            }
        }
        Path(tmp_dir.name, "elastic-config.json").write_text(
            json.dumps(config), encoding="utf-8"
        )
        old_cwd = os.getcwd()
        self.addCleanup(os.chdir, old_cwd)
        os.chdir(tmp_dir.name)

    def test_detecta_campos_extra_usando_nombres_recortados(self):
        header = header_normalizer(" l1,l2 , variant , Notas ")
        self.assertEqual(check_extra_fields(header), {"notas"})

    def test_no_detecta_extra_una_columna_ya_configurada(self):
        header = header_normalizer(" l1,l2 , variant ")
        self.assertEqual(check_extra_fields(header), set())


class PdfUploaderTests(SimpleTestCase):
    """``pdf_uploader`` no debe sobrescribir un PDF existente con el mismo nombre."""

    def setUp(self):
        tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(tmp_dir.cleanup)
        self.media = Path(tmp_dir.name, "media")
        self.media.mkdir()
        self.override = override_settings(BASE_DIR=tmp_dir.name, MEDIA_ROOT="/media/")
        self.override.enable()
        self.addCleanup(self.override.disable)

    def test_nombre_repetido_se_guarda_con_sufijo_sin_sobrescribir(self):
        primero = pdf_uploader(SimpleUploadedFile("x.pdf", b"uno"), "x.pdf")
        segundo = pdf_uploader(SimpleUploadedFile("x.pdf", b"dos"), "x.pdf")
        self.assertEqual(primero, "x.pdf")
        self.assertEqual(segundo, "x_1.pdf")
        self.assertEqual((self.media / "x.pdf").read_bytes(), b"uno")
        self.assertEqual((self.media / "x_1.pdf").read_bytes(), b"dos")
