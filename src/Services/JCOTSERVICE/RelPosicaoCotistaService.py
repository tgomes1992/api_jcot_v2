from .CotService import COTSERVICE
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET


class RelPosicaoCotistaService(COTSERVICE):
    url = "https://oliveiratrust.totvs.amplis.com.br:443/jcotserver/services/RelPosicaoCotistaService"

    '''o fundo é sempre um dicionário com o código do cun'''

    def bodyPosicaoCotista(self, dados):
        xml_request = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tot="http://totvs.cot.webservices" xmlns:glob="http://totvs.cot.webservices/global">
   <soapenv:Header>
   {self.header_login()}
</soapenv:Header>
   <soapenv:Body>
      <tot:obterRelPosCotistaRequest>
         <tot:filtro>
            <tot:cdCotista>{dados['cotista']}</tot:cdCotista>
            <tot:dtPosicao>{dados['data']}</tot:dtPosicao>
         </tot:filtro>
         <!--Optional:-->
         <glob:messageControl>
            <glob:user>{self.user}</glob:user>
            <glob:properties>
               <!--Zero or more repetitions:-->
               <glob:property name="?" value="?"/>
            </glob:properties>
         </glob:messageControl>
      </tot:obterRelPosCotistaRequest>
   </soapenv:Body>
</soapenv:Envelope>'''
        return xml_request
    
    def FormatarValores(self,body_str):
        dados = ET.fromstring(body_str)
        return dados
    
    def get_principal(self,body_str):
        corpo = self.FormatarValores(body_str)
        dados = []
        cd_cotista = corpo.find('.//{http://totvs.cot.webservices}cdCotista')
        fundos = corpo.findall('.//{http://totvs.cot.webservices}fundo')
        for fundo in fundos:
            base_dict ={}
            total_fundo = fundo.find(".//{http://totvs.cot.webservices}totalFundo")
            cd_fundo = fundo.find('.//{http://totvs.cot.webservices}cdFundo')
            for tag in total_fundo:
                # print (tag)
                base_dict[tag.tag.replace('{http://totvs.cot.webservices}', "")] =  tag.text
            base_dict['cd_fundo'] = cd_fundo.text.strip()
            base_dict['cd_cotista'] = cd_cotista.text.strip()
            dados.append(base_dict)
        return dados
     
     
    
    def formatar_xml_notas(self , nota):
       retorno_nota = {}
       for item in nota:
          retorno_nota[item.tag.replace("{http://totvs.cot.webservices}" , "")] =  item.text
        
       return retorno_nota
        
    def formatar_xml_fundos(self, fundo):
       retorno_fundo = {
          "nome_fundo":  fundo.find(".//{http://totvs.cot.webservices}nmFundo").text ,
          "valor_cota" :  fundo.find(".//{http://totvs.cot.webservices}vlCota").text , 
          "posicoes":  []
       }
       
       notas = fundo.findall('.//{http://totvs.cot.webservices}nota')
       
       retorno_nota = [self.formatar_xml_notas(item) for item in notas]
       
       retorno_fundo['posicoes'].extend(retorno_nota)
       
       return retorno_fundo
       
        
    def formatar_resposta_por_nota(self, string):
       dados = ET.fromstring(string)   
       print(dados)
       base_retorno = {
          "data": dados.find(".//{http://totvs.cot.webservices}dtPosicao").text , 
          "cd_cotista":  dados.find(".//{http://totvs.cot.webservices}cdCotista").text ,
          "nm_cotista":  dados.find(".//{http://totvs.cot.webservices}nmCotista").text ,

       }
       
       fundos = dados.findall(".//{http://totvs.cot.webservices}fundo")
       
       base_retorno['fundos'] = [self.formatar_xml_fundos(fundo) for fundo in fundos]
       
       
       
       return base_retorno
    
    def get_posicoes_json_nota(self, dados):
       base_request = requests.post(self.url, self.bodyPosicaoCotista(dados))

       return self.formatar_resposta_por_nota(base_request.content.decode("utf-8"))
        
      
    def request_jcot(self, dados):
        base_request = requests.post(self.url, self.bodyPosicaoCotista(dados))
        return self.get_principal(base_request.content.decode("utf-8"))

 


