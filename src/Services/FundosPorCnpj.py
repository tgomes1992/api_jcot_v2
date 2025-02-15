from .JCOTSERVICE import ListFundosService




class FundosPorCnpj():
    
    
    

    
    @staticmethod
    def codigosporcnpj( cnpj: str):
        service_list_fundos = ListFundosService("roboescritura" ,  "Senh@123")
        
        fundos = service_list_fundos.listFundoRequest()
        
        filtro = fundos['cnpj'] == cnpj
        
        return [item['codigo'] for item in fundos[filtro].to_dict("records")]        
        
         