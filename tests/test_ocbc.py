from monopoly.banks.ocbc import OCBC
from monopoly.enums import BankStatement


def test_ocbc_unprotected_pdf():
    pdf = OCBC(file_path="tests/ocbc_365.pdf")
    pdf.extract()

    assert pdf.df.columns.values.tolist() == [item for item in BankStatement]
    assert pdf.df.loc[0].to_dict() == {
        BankStatement.DATE: "12/06",
        BankStatement.DESCRIPTION: "FAIRPRICE FINEST SINGAPORE SG",
        BankStatement.AMOUNT: "18.49"
    }
    assert pdf.df.loc[1].to_dict() == {
        BankStatement.DATE: "12/06",
        BankStatement.DESCRIPTION: "DA PAOLO GASTRONOMIA SING — SINGAPORE SG",
        BankStatement.AMOUNT: "19.69"
    }
