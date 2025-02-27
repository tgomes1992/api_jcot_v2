from pydantic import BaseModel


class RetornoResponse(BaseModel):
    idNota: str 
    colLiqEstCust: str 
    dtAplicacao: str 
    dtLiquidacaoFisica: str 
    qtCotas: str 
    vlAplicacao: str 
    vlCorrigido: str 
    vlIof: str 
    vlAliquotaIof: str
    qtDiasDecorridoIof: str 
    vlIr: str 
    vlAliquotaIr: str
    qtDiasDecorridoIR: str 
    vlResgate: str 
    vlRendimento: str 
    pcResultado: str
    dtIofOuAniversario: str
    cdCotista: str
    nmCotista: str 
    cpfcnpjCotista: str 
    fundo: str 
    data: str 
    valor_cota: str 


