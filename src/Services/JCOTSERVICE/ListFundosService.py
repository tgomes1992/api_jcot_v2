from .CotService import COTSERVICE
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime


class ListFundosService(COTSERVICE):


    url = "https://oliveiratrust.totvs.amplis.com.br:443/jcotserver/services/FundosService"


    def listFundosRequestBody(self):
        xml_request = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tot="http://totvs.cot.webservices">
   <soapenv:Header>
        {self.header_login()}
   </soapenv:Header>
   <soapenv:Body>
      <tot:ListFundosRequest>
         <tot:fundo>
            <tot:login>{self.user}</tot:login>
         </tot:fundo>
      </tot:ListFundosRequest>
   </soapenv:Body>
</soapenv:Envelope>'''
        return xml_request


    def formatar_resposta(self,xmlresponse):
         base_formatacao = {
            'ns2:razaoSocial':  [] , 
            'ns2:cnpj': [] ,   
            'ns2:codigo':  [] , 
            'ns2:custodiante':  []  ,
            'ns2:gestorPrincipal': [] , 
            'ns2:administrador': []  , 
            'ns2:empresa':  [] , 
            'ns2:tipoFundo': [] , 
            'ns2:dataPosicao': []  ,
         }
         response = BeautifulSoup(xmlresponse,'xml')
         fundos = response.find_all("ns2:fundo")
         for i in fundos:
            formata_data = datetime.strptime(i.find('ns2:dataPosicao').text[0:10],'%Y-%m-%d')
            base_formatacao['ns2:razaoSocial'].append(self.get_bs4_tag_text(i.find('ns2:razaoSocial')))
            base_formatacao['ns2:cnpj'].append(self.get_bs4_tag_text(i.find('ns2:cnpj')))
            base_formatacao['ns2:codigo'].append(self.get_bs4_tag_text(i.find('ns2:codigo'))) 
            base_formatacao['ns2:custodiante'].append(self.get_bs4_tag_text(i.find('ns2:custodiante')))
            base_formatacao['ns2:gestorPrincipal'].append(self.get_bs4_tag_text(i.find('ns2:gestorPrincipal')))
            base_formatacao['ns2:administrador'].append(self.get_bs4_tag_text(i.find('ns2:administrador')))
            base_formatacao['ns2:empresa'].append(self.get_bs4_tag_text(i.find('ns2:empresa')))
            base_formatacao['ns2:tipoFundo'].append(self.get_bs4_tag_text(i.find('ns2:tipoFundo')))
            base_formatacao['ns2:dataPosicao'].append(i.find('ns2:dataPosicao').text[0:10])
         df = pd.DataFrame.from_dict(base_formatacao)
         df.columns = ["razaoSocial",'cnpj' , 'codigo','custodiante','gestorPrincipal',"administrador",'empresa',"tipoFundo","dataPosicao" ]
         return df 
    

    def get_bs4_tag_text(self , tag_name ):
        try:
            return tag_name.text
        except:
            return "na"
        



    def listFundoRequest(self):
        base_request = requests.post(self.url, self.listFundosRequestBody())
        return self.formatar_resposta(base_request.content)


