from .CotService import COTSERVICE
import requests
from bs4 import BeautifulSoup
import pandas as pd
import xml.etree.ElementTree as ET


class RelPosicaoFundoCotistaService(COTSERVICE):
    url = "https://oliveiratrust.totvs.amplis.com.br:443/jcotserver/services/RelPosicaoFundoCotistaService"

    '''o fundo é sempre um dicionário com o código do cun'''

    def relPosicaoFundoCotistaBody(self, fundo):
        xml_request = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tot="http://totvs.cot.webservices" xmlns:glob="http://totvs.cot.webservices/global">
   <soapenv:Header>
                {self.header_login()}
   </soapenv:Header>
   <soapenv:Body>
      <tot:obterRelPosFundoCotistaRequest>
         <tot:filtro>
            <tot:cdFundo>{fundo['codigo']}</tot:cdFundo>   
            <tot:dtPosicao>{fundo['dataPosicao']}</tot:dtPosicao>
         </tot:filtro>
         <!--Optional:-->
         <glob:messageControl>
            <glob:user>{self.user}</glob:user>
            <!--Optional:-->
            <glob:sessionID>?</glob:sessionID>
            <!--Optional:-->
            <glob:messageID>?</glob:messageID>
            <glob:remoteAddr>?</glob:remoteAddr>
            <!--Optional:-->
            <glob:channel>?</glob:channel>
            <!--Optional:-->
            <glob:properties>
               <!--Zero or more repetitions:-->
               <glob:property name="?" value="?"/>
            </glob:properties>
         </glob:messageControl>
      </tot:obterRelPosFundoCotistaRequest>
   </soapenv:Body>
</soapenv:Envelope>'''
        return xml_request

    def RelPosicaoFundoCotistaServiceRequest(self, fundo):
        base_request = requests.post(self.url, self.relPosicaoFundoCotistaBody(fundo))

        return base_request.content.decode("utf-8")

    def get_status(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)
        soup = BeautifulSoup(xml, "xml")
        try:
            status = soup.find("ns2:statusFundo").text
            return status
        except:
            return "Fundo não disponível para consulta"

    def get_cotistas(self, xml_part):
        cotistas = xml_part.find_all("ns2:cotista")
        return cotistas
    
    def get_cotistas_ET(self, xml_part):
        cotistas = xml_part.find_all("ns2:cotista")
        return cotistas


    def get_posicoes_cotistas(self, xml_part):


        total_cotistas = xml_part.find("ns2:totalCotista")
        for item in xml_part:
            print (item)

        posicao = {
            "cd_cotista": xml_part.find("ns2:cdCotista").text,
            "nmCotista": xml_part.find("ns2:nmCotista").text,
            # "cpfcnpjCotista": xml_part.find("ns2:cpfcnpjCotista").text,
            "qtCotas": float(total_cotistas.find("ns2:qtCotas").text),
            "vlAplicacao": float(total_cotistas.find("ns2:vlAplicacao").text),
            "vlCorrigido": float(total_cotistas.find("ns2:vlCorrigido").text),
            "vlIof": float(total_cotistas.find("ns2:vlIof").text),
            "vlIr": float(total_cotistas.find("ns2:vlIr").text),
            "vlResgate": float(total_cotistas.find("ns2:vlResgate").text),
            "vlRendimento": float(total_cotistas.find("ns2:vlRendimento").text),
        }

        return posicao
    
    def get_posicoes_cotistas_ET(self, xml_part , fundo ,  cota):
        total_cotista = xml_part.find('{http://totvs.cot.webservices}totalCotista')
        try:
            retorno_cotista = {       
            "cd_cotista": xml_part.find("{http://totvs.cot.webservices}cdCotista").text,
            "nmCotista": xml_part.find("{http://totvs.cot.webservices}nmCotista").text,
            "cpfcnpjCotista": xml_part.find("{http://totvs.cot.webservices}cpfcnpjCotista").text
            }
        except Exception as e:
            
            retorno_cotista = {       
            "cd_cotista": xml_part.find("{http://totvs.cot.webservices}cdCotista").text,
            "nmCotista": xml_part.find("{http://totvs.cot.webservices}nmCotista").text,
            "cpfcnpjCotista": "2332886000104"
            }


        for item in total_cotista.iter():
            retorno_cotista[item.tag.replace("{http://totvs.cot.webservices}" , "")] =  item.text

        
        retorno_cotista['fundo'] = fundo['codigo']
        retorno_cotista['data'] = fundo['dataPosicao']
        retorno_cotista['valor_cota'] = cota
 
        return retorno_cotista
    
    
    def get_posicoes_cotistas_ET_nota(self, xml_part , fundo ,  cota):
        total_cotista = xml_part.find('{http://totvs.cot.webservices}totalCotista')
        

        
        
        cd_cotista =  xml_part.find("{http://totvs.cot.webservices}cdCotista").text

        nmCotista =  xml_part.find("{http://totvs.cot.webservices}nmCotista").text
        cpfcnpjCotista = xml_part.find("{http://totvs.cot.webservices}cpfcnpjCotista").text
        
        notas = xml_part.findall(".//{http://totvs.cot.webservices}nota")
        
        notas_dict = []
        
        for nota in notas:

            ndict = {}
            for item in nota:
                ndict[item.tag.replace("{http://totvs.cot.webservices}" , "")] =  item.text
            notas_dict.append(ndict)

            
        retorno_cotista = pd.DataFrame.from_dict(notas_dict)


        
        retorno_cotista['cdCotista'] = cd_cotista 
        retorno_cotista['nmCotista'] = nmCotista
        retorno_cotista['cpfcnpjCotista'] = cpfcnpjCotista
        retorno_cotista['fundo'] = fundo['codigo']
        retorno_cotista['data'] = fundo['dataPosicao']
        retorno_cotista['valor_cota'] = cota
 
 
        return retorno_cotista.to_dict("records")
    

    def get_cd_cotistas(self, xml):
        cd_cotista = xml.find("ns2:cdCotista").text.strip()
        return cd_cotista

    def get_lista_cotistas(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)
        soup = BeautifulSoup(xml, "xml")
        cotistas = self.get_cotistas(soup)
        lista_cotistas = [{"cotista": self.get_cd_cotistas(item)} for item in cotistas]
        return lista_cotistas

    def get_posicoes(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)
        soup = BeautifulSoup(xml, "xml")
        cotistas = self.get_cotistas(soup)
        posicoes = [self.get_posicoes_cotistas_ET(item) for item in cotistas]
        return posicoes
    
    def get_posicoes_ET(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)
        element = ET.fromstring(xml)
        valor_cota = ""
        for valor in element.iter("{http://totvs.cot.webservices}fundo"):
            valor_cota = valor.find("{http://totvs.cot.webservices}vlCota").text

        cotistas = [item for item in element.iter('{http://totvs.cot.webservices}cotista')]       
        posicoes = [self.get_posicoes_cotistas_ET(cotista , fundo ,  valor_cota) for cotista in cotistas] 
        return posicoes
    
    
    def get_posicoes_ET_nota(self, fundo):
        retorno = []
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)
        element = ET.fromstring(xml)
        valor_cota = ""
        for valor in element.iter("{http://totvs.cot.webservices}fundo"):
            valor_cota = valor.find("{http://totvs.cot.webservices}vlCota").text

        cotistas = [item for item in element.findall('.//{http://totvs.cot.webservices}cotista')]       

        posicoes = [self.get_posicoes_cotistas_ET_nota(cotista , fundo ,  valor_cota) for cotista in cotistas] 
        
        for item in posicoes:
            retorno.extend(item)
        
        return retorno

    def get_posicoes_table(self, fundo):
        base_dados = self.get_posicoes(fundo)
        df = pd.DataFrame.from_dict(base_dados)
        return df

    def get_posicoes_json(self, fundo):
        return self.get_posicoes_ET(fundo)
    
    
    def get_posicoes_json_nota(self, fundos:list):
        
        resultado = []
        
        for fundo in fundos:
            resultado.extend(self.get_posicoes_ET_nota(fundo))
        
        return resultado
    
    

    def get_posicao_fundo(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)
        try:
            soup = BeautifulSoup(xml, 'xml')
            total_fundo = soup.find("ns2:totalFundos")
            valor = {
                "fundo": fundo['codigo'],
                "valor": float(total_fundo.find("ns2:qtCotas").text)
            }
        except :
            valor = {
                "fundo":  fundo['codigo'],
                "valor":  0
            }
        return valor

    def get_qtd_fundo(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)
        try:
            soup = BeautifulSoup(xml, 'xml')

            total_fundo = soup.find("ns2:totalFundos")
            valor = float(total_fundo.find("ns2:qtCotas").text)
        except:
            valor = 0
        return valor

    def get_posicao_consolidada(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)

        try:
            soup = BeautifulSoup(xml, 'xml')
            total_fundo = soup.find("ns2:totalFundos")
            dict_base = {
                "qtCotas": [float(total_fundo.find("ns2:qtCotas").text)],
                "vlAplicacao": [float(total_fundo.find("ns2:vlAplicacao").text)],
                "vlCorrigido": [float(total_fundo.find("ns2:vlCorrigido").text)],
                "vlIof": [float(total_fundo.find("ns2:vlIof").text)],
                "vlIr": [float(total_fundo.find("ns2:vlIr").text)],
                "vlResgate": [float(total_fundo.find("ns2:vlResgate").text)],
                "vlRendimento": [float(total_fundo.find("ns2:vlRendimento").text)]
            }


        except:
            dict_base = {
                "qtCotas": [0],
                "vlAplicacao": [0],
                "vlCorrigido": [0],
                "vlIof":[ 0],
                "vlIr": [0],
                "vlResgate":[ 0],
                "vlRendimento":[ 0]
            }

        return dict_base

    def get_valor_cota(self, fundo):
        xml = self.RelPosicaoFundoCotistaServiceRequest(fundo)

        element = ET.fromstring(xml)
        valor_cota = ""
        for valor in element.iter("{http://totvs.cot.webservices}fundo"):
            valor_cota = valor.find("{http://totvs.cot.webservices}vlCota").text
        return valor_cota



