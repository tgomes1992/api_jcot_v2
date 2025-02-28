from fastapi import FastAPI , HTTPException
from datetime import date 
from fastapi import FastAPI
from Services import *
from dotenv import load_dotenv
import os
from models import RetornoResponse


load_dotenv()



app = FastAPI(
    title="API - POSIÇÕES ESCRITURAIS",
    description="Api responsável pela concentração de posições escriturais por cautela para fundos de investimento",
    version="1.0.0",
)



@app.get("/statusPassivo", tags=["Status Passivo"]  ,summary="Status do Passivo dos Fundos de Investimento" ,

         description="Retorna a data disponível de um fundo e suas classes no passivo de fundos de investimento da Oliveira Trust" )
async def statuspassivo():

    fundos = ListFundosService(os.getenv("JCOT_USER"), os.getenv("JCOT_PASSWORD"))
    print ("ar")
  
    '''Retorna a consulta de movimentação diária por cnpj de fundo e por data'''
    return {"dados":  fundos.listFundoRequest().to_dict("records")}





@app.get("/movimentacao", tags=["Movimentação"]  ,summary="Consulta de Movimentação" ,

                          description="Consulta de Movimentação no Jcot por cnpj de fundo" )
async def movimentacaocot(data: date  ,  cnpj: str):
    print ('r')
    fundos = FundosPorCnpj.codigosporcnpj(cnpj)
    
    retorno = []
    service_movimentacao = ConsultaMovimentoPeriodoV2Service(os.getenv("JCOT_USER"), 
                                                             os.getenv("JCOT_PASSWORD"))
  
    fundos = [{"data_inicial": str(data),
                            "data_final": str(data), 
                            "cd_fundo": fundo} for fundo in fundos]
    for item in fundos:
        movimentos = service_movimentacao.movimento_diario_request(item)
        retorno.extend(movimentos)
  
  
    '''Retorna a consulta de movimentação diária por cnpj de fundo e por data'''
    return retorno






@app.get("/posicao-fundo" , tags=["Posição"] ,      
                                summary="Consulta de Posição no jcot por cnpj de fundo" ,
                          description="Consulta de Posição no Jcot por cnpj de fundo" )
async def posicaojcot(data: date  ,  cnpj: str ):
    '''Retorna a consulta de posição diária por cnpj de fundo e por data'''
    print ('aq')
    try:

        fundos = FundosPorCnpj.codigosporcnpj(cnpj)

        service_jcot = RelPosicaoFundoCotistaService("roboescritura",
                                                     os.getenv("JCOT_PASSWORD"))

        lista_fundos = [{"dataPosicao": str(data), "codigo": fundo} for fundo in fundos]
        posicoes = service_jcot.get_posicoes_json_nota(lista_fundos)
        retorno = []




        return posicoes

    except Exception as ex:
        print (ex)
        raise HTTPException(status_code=500, detail=str(ex))



@app.get("/posicao-investidor" , tags=["Posição"] , summary="Consulta de Posição no jcot por código do investidor" , 
                          description="Consulta de Posição no Jcot por cd do investidor")
async def posicaojcotx(data: date  ,  cd_cotista: str ):
    '''Retorna a consulta de posição diária por cnpj de fundo e por data'''
    
    service_posicao = RelPosicaoCotistaService(os.getenv("JCOT_USER"),
                                               os.getenv("JCOT_PASSWORD"))

    dados = {"cotista": cd_cotista,'data': str(data)}     
    
    try:                   

        posicoes = service_posicao.get_posicoes_json_nota(dados)
        
        return {"dados":  posicoes}
    
    except:
        return {"dados": "Não há posições para o dia solicitado"}

