from fastapi import FastAPI , HTTPException , Query
from datetime import date 
from fastapi import FastAPI
from Services import *
from dotenv import load_dotenv
import os
from models import RetornoPosicaoResponse
from typing import List
import logging
import logging.config

load_dotenv()

# Set the basic configuration
LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s %(asctime)s - %(name)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        # Configure the root logger
        "": {"handlers": ["console"], "level": "INFO"},
        # Optionally configure FastAPI or uvicorn loggers explicitly
        "uvicorn": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}

logging.config.dictConfig(LOGGING_CONFIG)


# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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






@app.get(
    "/posicao-fundo",
    tags=["Posição"],
    summary="Consulta de Posição no jcot por CNPJ de fundo",
    description="Consulta de Posição no JCOT por CNPJ de fundo",
    response_model=List[RetornoPosicaoResponse]
)
async def posicaojcot(data: date = Query(..., description="Data da posição (YYYY-MM-DD)"),
                      cnpj: str = Query(..., description="CNPJ do fundo")):
    """Retorna a consulta de posição diária por CNPJ de fundo e por data"""

    try:
        logger.info(f"Recebida solicitação para data {data} e CNPJ {cnpj}")

        # Verifica se o CNPJ está no formato correto
        if not cnpj.isdigit() or len(cnpj) not in [14, 18]:
            raise HTTPException(
                status_code=400,
                detail="O CNPJ deve conter apenas números e ter 14 ou 18 caracteres."
            )

        # Obtém os códigos dos fundos a partir do CNPJ
        try:
            fundos = FundosPorCnpj.codigosporcnpj(cnpj)
            if not fundos:
                raise HTTPException(
                    status_code=404,
                    detail=f"Nenhum fundo encontrado para o CNPJ {cnpj}."
                )
        except Exception as e:
            logger.error(f"Erro ao buscar fundos por CNPJ {cnpj}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao buscar fundos. Verifique o CNPJ ou tente novamente mais tarde."
            )

        # Verifica credenciais do serviço
        usuario = os.getenv("JCOT_USER")
        senha = os.getenv("JCOT_PASSWORD")

        if not usuario or not senha:
            raise HTTPException(
                status_code=500,
                detail="Credenciais do serviço JCOT não configuradas corretamente."
            )

        service_jcot = RelPosicaoFundoCotistaService(usuario, senha)

        lista_fundos = [{"dataPosicao": str(data), "codigo": fundo} for fundo in fundos]

        try:
            posicoes = service_jcot.get_posicoes_json_nota(lista_fundos)
            if not posicoes:
                raise HTTPException(
                    status_code=404,
                    detail="Nenhuma posição encontrada para os fundos informados."
                )
        except Exception as e:
            logger.error(f"Erro ao consultar posições no JCOT: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erro ao consultar posições no JCOT. Tente novamente mais tarde."
            )

        logger.info("Consulta realizada com sucesso")
        retorno = []
        for item in posicoes:
            posicao = RetornoPosicaoResponse(**item)
            retorno.append(posicao)
        return retorno

    except HTTPException as http_ex:
        raise http_ex
    except Exception as ex:
        logger.error(f"Erro inesperado: {str(ex)}")
        raise HTTPException(
            status_code=500,
            detail="Ocorreu um erro inesperado. Contate o suporte."
        )




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

