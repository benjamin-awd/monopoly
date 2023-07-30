from monopoly.banks.ocbc import OCBC
import os


def main():
    for item in os.listdir("pdf/ocbc/365"):
        pdf = OCBC(f"pdf/ocbc/365/{item}")
        pdf.extract()

main()