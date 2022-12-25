from pdf import PDF
import os


def main():
    df_list = []
    for item in os.listdir("src/pdf/citibank"):
        print(item)
        pdf = PDF(f"src/pdf/citibank/{item}")
        pdf.extract()
        pdf.transform()
        df_list.append(pdf.df)

main()