#!/usr/bin/env python

import logging
import os
import sys

from pyhanko.pdf_utils.crypt import SecurityHandlerVersion
from pyhanko.pdf_utils.reader import PdfFileReader

logger = logging.getLogger(__name__)


class PdfHashExtractor:
    def __init__(self, file_name):
        self.file_name = file_name

        with open(file_name, "rb") as doc:
            pdf = PdfFileReader(doc, strict=False)
            self.document_id = pdf.document_id
            self.encryption_params = pdf._get_encryption_params()
            self.trailer = pdf.trailer
            self.pdf_spec = pdf._header_version
            self.security_handler = pdf.security_handler

    def parse(self):
        algorithm = self.encryption_params["/V"]
        revision = self.encryption_params["/R"]
        length = self.encryption_params["/Length"]
        permissions = self.encryption_params["/P"]

        document_id = self.document_id[0].hex()
        passwords = self.get_passwords()

        output = (
            "$pdf$" + str(algorithm) + "*" + str(revision) + "*" + str(length) + "*"
        )

        output += (
            str(permissions)
            + "*"
            + str(int(self.security_handler.encrypt_metadata))
            + "*"
        )
        output += str(int(len(document_id) / 2)) + "*" + document_id + "*" + passwords
        logger.info("Hash: %s", output)

        return output

    def get_passwords(self):
        output = ""
        encryption_keys = ["/U", "/O"]

        # Support for PDF-1.7
        if self.pdf_spec == (1, 7):
            encryption_keys.extend(["/UE", "/OE"])

        for key in encryption_keys:
            data = self.encryption_params.get(key, b"")

            if key in ("/O", "/U"):
                logger.info(
                    "Security handler version: %s", self.security_handler.version
                )
                if self.security_handler.version == SecurityHandlerVersion.AES256:
                    data = data[:40]

                # Legacy support for older PDF specifications
                if (
                    self.security_handler.version
                    <= SecurityHandlerVersion.RC4_OR_AES128
                ):
                    data = data[:32]

            output += str(int(len(data))) + "*" + data.hex() + "*"

        return output


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.error(f"Usage: {os.path.basename(sys.argv[0])} <PDF file(s)>")
        sys.exit(-1)

    for j in range(1, len(sys.argv)):
        filename = sys.argv[j]
        logger.info(f"Analyzing {filename}")
        extractor = PdfHashExtractor(filename)

        try:
            result = extractor.parse()
            print(result)
        except RuntimeError as e:
            logger.error(f"{filename} : {str(e)}")
