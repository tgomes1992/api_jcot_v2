from .CotService import COTSERVICE
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
pd.options.display.float_format = '{:,.2f}'.format

from datetime import datetime

class RelAnaliticoCotistaFundo(COTSERVICE):

    url = 'https://oliveiratrust.totvs.amplis.com.br:443/jcotserver/services/RelMovAnaliticoFundoCotistaService'
    def body_buscar_relatorio(self , dados):
        data = f'''
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tot="http://totvs.cot.webservices" xmlns:glob="http://totvs.cot.webservices/global">
      <soapenv:Header>
            {self.header_login()}
   </soapenv:Header>
   <soapenv:Body>
      <tot:obterRelMovAnaliticoFundoCotistaRequest>
         <tot:filtro>
            <!--Optional:-->
            <tot:cdFundo>{dados['cd_fundo']}</tot:cdFundo>
            <tot:dtInicial>{dados['data_inicial']}</tot:dtInicial>
            <tot:dtFinal>{dados['data_final']}</tot:dtFinal>
         </tot:filtro>
         <!--Optional:-->
         <glob:messageControl>
            <glob:user>{self.user}</glob:user>
            <glob:properties>
               <!--Zero or more repetitions:-->
               <glob:property name="?" value="?"/>
            </glob:properties>
         </glob:messageControl>
      </tot:obterRelMovAnaliticoFundoCotistaRequest>
   </soapenv:Body>
</soapenv:Envelope>'''
        return data

    def formatar_resposta(self ,  xml_string, dados):
        movimentos = []
        root = ET.fromstring(xml_string)
        try:
            cotistas = root.findall(".//{http://totvs.cot.webservices}cotista")
            cd_fundo = root.find(".//{http://totvs.cot.webservices}cdFundo").text
            total_cotistas = []
            for cotista in cotistas:
                base = {
                    'cd_cotista': cotista.find(".//{http://totvs.cot.webservices}cdCotista").text ,
                    'cpfCnpj': cotista.find(".//{http://totvs.cot.webservices}noCpfCnpj").text ,
                    "aplicacao_principal": cotista.find(".//{http://totvs.cot.webservices}totalAplicacaoCotista").find('.//{http://totvs.cot.webservices}vlOriginal').text ,
                    "aplicao_operacao": cotista.find(".//{http://totvs.cot.webservices}totalAplicacaoCotista").find('.//{http://totvs.cot.webservices}vlOperacao').text ,
                    "resgate_principal": cotista.find(".//{http://totvs.cot.webservices}totalResgatesCotista").find('.//{http://totvs.cot.webservices}vlOriginal').text,
                    "resgate_operacao": cotista.find(".//{http://totvs.cot.webservices}totalResgatesCotista").find('.//{http://totvs.cot.webservices}vlOperacao').text ,
                    "data_final": datetime.strptime(dados['data_final'] ,  "%Y-%m-%d") ,
                    "cd_fundo":  cd_fundo
            }
                total_cotistas.append(base)
            pd.DataFrame.from_dict(total_cotistas).to_excel("relatorio.xlsx")
            return total_cotistas
        except Exception as e:
            print (e)
            pass



    def formatar_notas(self, notas_xml):
        base_formatado = []

        for nota in notas_xml:
            data = {
                "notaOperacao": nota.find(".//{http://totvs.cot.webservices}notaOperacao").text,
                "notaAplicacao": nota.find(".//{http://totvs.cot.webservices}notaAplicacao").text,
                "dsFormaLiquidacao": nota.find(".//{http://totvs.cot.webservices}dsFormaLiquidacao").text,
                "tpLiquidacao": nota.find(".//{http://totvs.cot.webservices}tpLiquidacao").text,
                "dsContaLiquidacao": nota.find(".//{http://totvs.cot.webservices}dsContaLiquidacao").text,
                "qtdCotas": float(nota.find(".//{http://totvs.cot.webservices}qtdCotas").text),
                "vlOriginal": float(nota.find(".//{http://totvs.cot.webservices}vlOriginal").text),
                "vlOperacao": float(nota.find(".//{http://totvs.cot.webservices}vlOperacao").text),
                "vlIR": float(nota.find(".//{http://totvs.cot.webservices}vlIR").text),
                "vlPenaltyFee": float(nota.find(".//{http://totvs.cot.webservices}vlPenaltyFee").text),
                "vlReceitaSaqueCarencia": float(nota.find(".//{http://totvs.cot.webservices}vlReceitaSaqueCarencia").text),
                "vlIOF": float(nota.find(".//{http://totvs.cot.webservices}vlIOF").text),
                "vlLiquido": float(nota.find(".//{http://totvs.cot.webservices}vlLiquido").text)
            }
            base_formatado.append(data)

        return  base_formatado

    def notas_ajuste(self):
        pass


    def formatar_movimentos(self, lista_movimentos):
        retorno = []
        for movimento_xml in lista_movimentos:
            tipo = movimento_xml.find(".//{http://totvs.cot.webservices}tpMovimento").text
            notas = movimento_xml.findall(".//{http://totvs.cot.webservices}nota")
            notas_formatadas = self.formatar_notas(notas)
            for nota in notas_formatadas:
                retorno.append(nota)

        return retorno


    def ajuste_movimentos(self , data ,  cd_cotista ,  notas):
        nnotas = []
        for nota in notas:
            nota['data'] = datetime.strptime(data , "%Y-%m-%d")
            nota['cotista'] = cd_cotista

            nnotas.append(nota)

        return nnotas


    def formatar_datas(self , xml_content):
        root = ET.fromstring(xml_content)

        datas = root.findall(".//{http://totvs.cot.webservices}data")

        base = []
        try:
            for data in datas:


                cd_fundo = root.find(".//{http://totvs.cot.webservices}cdFundo").text
                data_mov = data.find(".//{http://totvs.cot.webservices}dtMovimento").text


                clearing = data.find(".//{http://totvs.cot.webservices}clearing")
                cotista = clearing.find(".//{http://totvs.cot.webservices}cotista")
                cd_cotista = cotista.find(".//{http://totvs.cot.webservices}cdCotista").text

                movimentos = data.findall(".//{http://totvs.cot.webservices}movimento")
                movimentos_ajustados = self.formatar_movimentos(movimentos)
                movimentos_formatados = self.ajuste_movimentos(data_mov,  cd_cotista, movimentos_ajustados)
                for movimento in movimentos_formatados:
                    base.append(movimento)
        except Exception as e:
            print (e)

        return base


    def get_dados_cotistas(self, xml_string):
        movimentos  = []
        pass

    def get_movimento_periodo_request(self , dados):
        base_request = requests.post(self.url, self.body_buscar_relatorio(dados))
        movimentos = self.formatar_resposta(base_request.content.decode('utf-8'), dados )

        return movimentos

    def get_movimentos_detalhados(self, dados):
        base_request = requests.post(self.url, self.body_buscar_relatorio(dados))
        movimentos_detalhados = self.formatar_datas(base_request.content.decode('utf-8') )
        return movimentos_detalhados