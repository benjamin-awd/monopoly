from monopoly.banks.ocbc import OCBC


def test_ocbc_unprotected_pdf():
    pdf = OCBC(file_path="tests/ocbc_365.pdf")
    pdf.extract()

    assert pdf.df.columns.values.tolist() == ["Date", "Description", "Amount"]
    assert pdf.df.loc[0].to_dict() == {
        "Date": "12/06",
        "Description": "FAIRPRICE FINEST SINGAPORE SG",
        "Amount": "18.49"
    }
    assert pdf.df.loc[1].to_dict() == {
        "Date": "12/06",
        "Description": "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
        "Amount": "19.69"
    }
