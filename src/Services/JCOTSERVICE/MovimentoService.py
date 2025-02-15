from .CotService import COTSERVICE
from bs4 import BeautifulSoup
import requests




class MovimentoServicebase(COTSERVICE):


    url =  "https://oliveiratrust.totvs.amplis.com.br:443/jcotserver/services/MovimentoService"


    def excluir_nota_body(self ,  nota):
        body_excluir = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tot="http://totvs.cot.webservices" xmlns:glob="http://totvs.cot.webservices/global">
   <soapenv:Header>
        {self.header_login()}
      </soapenv:Header>
   <soapenv:Body>
      <tot:excluirMovimentoRequest>
         <tot:movimentoExcluir>
            <tot:idNota>{nota}</tot:idNota>
            <!--Optional:-->
            <glob:messageControl>
               <glob:user>{self.user}</glob:user>
               <glob:properties>
                  <!--Zero or more repetitions:-->
                  <glob:property name="?" value="?"/>
               </glob:properties>
            </glob:messageControl>
         </tot:movimentoExcluir>
         <!--Optional:-->
         <glob:messageControl>
            <glob:user>{self.user}</glob:user>
            <glob:properties>
               <!--Zero or more repetitions:-->
               <glob:property name="?" value="?"/>
            </glob:properties>
         </glob:messageControl>
      </tot:excluirMovimentoRequest>
   </soapenv:Body>
</soapenv:Envelope>'''

        return body_excluir

    def formatar_resposta(self ,  xml_resposta):
        soup = BeautifulSoup(xml_resposta, 'xml')
        resultado = soup.find('ns2:desc').text
        return {
            'resposta' : resultado
        }


    def ExcluirNotaRequest(self , nota):
        base_request = requests.post(self.url, self.excluir_nota_body(nota))
        return self.formatar_resposta(base_request.content)


