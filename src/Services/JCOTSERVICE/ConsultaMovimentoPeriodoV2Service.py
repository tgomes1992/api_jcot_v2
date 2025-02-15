from .CotService import COTSERVICE
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import xml.etree.ElementTree as ET
pd.options.display.float_format = '{:,.2f}'.format

class ConsultaMovimentoPeriodoV2Service(COTSERVICE):


    url = "https://oliveiratrust.totvs.amplis.com.br:443/jcotserver/services/ConsultaMovimentoPeriodoV2Service"


    def movimento_body(self , dados ):
      base  = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tot="http://totvs.cot.webservices" xmlns:glob="http://totvs.cot.webservices/global">
   <soapenv:Header>
      {self.header_login()}
   </soapenv:Header>
   <soapenv:Body>
      <tot:consultaMovimentoPeriodoV2Request>
         <!--Optional:-->
         <tot:filtro>
            <tot:cdFundo>{dados['cd_fundo']}</tot:cdFundo>
            <tot:dtInicial>{dados['data']}</tot:dtInicial>
            <tot:dtFinal>{dados['data']}</tot:dtFinal>
            <tot:cdTipoMov>{dados['movimento']}</tot:cdTipoMov>          
            <tot:cdTipoConsulta>E</tot:cdTipoConsulta>
         </tot:filtro>
         <!--Optional:-->
         <glob:messageControl>
            <glob:user>{self.user}</glob:user>
            <!--Optional:-->
            <glob:properties>
               <!--Zero or more repetitions:-->
               <glob:property name="?" value="?"/>
            </glob:properties>
         </glob:messageControl>
      </tot:consultaMovimentoPeriodoV2Request>
   </soapenv:Body>
</soapenv:Envelope>'''
      return base

    def movimento_body_periodo(self, dados):
          base = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tot="http://totvs.cot.webservices" xmlns:glob="http://totvs.cot.webservices/global">
       <soapenv:Header>
          {self.header_login()}
       </soapenv:Header>
       <soapenv:Body>
          <tot:consultaMovimentoPeriodoV2Request>
             <!--Optional:-->
             <tot:filtro>
                <tot:cdFundo>{dados['cd_fundo']}</tot:cdFundo>
                <tot:dtInicial>{dados['data_inicial']}</tot:dtInicial>
                <tot:dtFinal>{dados['data_final']}</tot:dtFinal>
                <tot:cdTipoMov>{dados['movimento']}</tot:cdTipoMov>          
                <tot:cdTipoConsulta>E</tot:cdTipoConsulta>
             </tot:filtro>
             <!--Optional:-->
             <glob:messageControl>
                <glob:user>{self.user}</glob:user>
                <!--Optional:-->
                <glob:properties>
                   <!--Zero or more repetitions:-->
                   <glob:property name="?" value="?"/>
                </glob:properties>
             </glob:messageControl>
          </tot:consultaMovimentoPeriodoV2Request>
       </soapenv:Body>
    </soapenv:Envelope>'''
          return base




    def formatar_resposta(self , xml_content , cnpj_fundo):

            movimentos = []

            xml_element = ET.fromstring(xml_content)
            print ( cnpj_fundo ,xml_content)
            for movimento in xml_element.iter("{http://totvs.cot.webservices}movimento"):
                # print(movimento.tag)
                item = {}
                item['Numero Operacao'] = movimento.find("{http://totvs.cot.webservices}idNota").text
                item['Investidor'] =  movimento.find("{http://totvs.cot.webservices}nmCotista").text
                item["Papel Cota"] = movimento.find("{http://totvs.cot.webservices}nmFundo").text.strip()
                item['Tipo Operacao'] = movimento.find("{http://totvs.cot.webservices}dsTipoMov").text.replace("Ç" , "C").replace("Ã" , "A")
                item['Data Operacao'] =  datetime.strptime(movimento.find("{http://totvs.cot.webservices}dtMov").text , "%Y-%m-%d").strftime("%d/%m/%Y")
                item['Data Conversao'] =  datetime.strptime(movimento.find("{http://totvs.cot.webservices}dtLiqFisica").text  , "%Y-%m-%d").strftime("%d/%m/%Y")
                item['Data Liquidacao'] = datetime.strptime(movimento.find("{http://totvs.cot.webservices}dtLiqFinanceira").text , "%Y-%m-%d").strftime("%d/%m/%Y")
                item['Valor'] =  movimento.find("{http://totvs.cot.webservices}vlBruto").text
                item['Status'] = "Batido"
                item['Status Conversao'] = "Nao Efetivado"
                item['Data do Fundo na Movimentacao'] =  datetime.strptime(movimento.find("{http://totvs.cot.webservices}dtMov").text ,"%Y-%m-%d").strftime("%d/%m/%Y")
                movimentos.append(item)
                item["CNPJ do fundo"] = cnpj_fundo

            return movimentos


    def formatar_resposta_periodo(self , xml_content):

            movimentos = []

            xml_element = ET.fromstring(xml_content)

            for movimento in xml_element.iter("{http://totvs.cot.webservices}movimento"):
                ndict  = {}

                for item in movimento:
                   ndict[item.tag.replace('{http://totvs.cot.webservices}' , '')] = item.text
      
      
                movimentos.append(ndict)

            return movimentos

    def get_movimento_request(self , dados):
        base_request = requests.post(self.url, self.movimento_body(dados))
        return self.formatar_resposta(base_request.content.decode('utf-8') ,  dados['cnpj_fundo'])

    def get_movimento_periodo_request(self , dados):
        base_request = requests.post(self.url, self.movimento_body_periodo(dados))


        movimentos = self.formatar_resposta_periodo(base_request.content.decode('utf-8'))
        return movimentos
     
     
    def movimento_diario_request(self , dados ):
        resultado = []
        
        dados['movimento'] = 'A'
        
        aplicacaoes = requests.post(self.url, self.movimento_body_periodo(dados))

        resultado.extend(self.formatar_resposta_periodo(aplicacaoes.content))
        
        dados['movimento'] = 'R'
        
        resgates = requests.post(self.url, self.movimento_body_periodo(dados))

        resultado.extend(self.formatar_resposta_periodo(resgates.content))
        
        
        return resultado
     
     

    def montar_retorno_xp(self, lista_de_fundos):
      final_report = []
      for fundo in lista_de_fundos:      
         dados = self.get_movimento_request(fundo)
         for lista in dados:
               final_report.append(lista)
      return pd.DataFrame.from_dict(final_report)
