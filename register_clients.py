# needed fields to fill a form of a new client as a dict
# fields = Names	Emails	Money	Markets	(=>Symbol)	risk (=>Optimization)
# Symbol is giben by the Market, and Optimization by risk too
import pandas as pd

print("Register Clients to generate portfolios according their specs\n\n\n".center(60,'+'))
client_form = {'Names':[],'Emails':[],'Markets':[],'Symbol':[],'Money':[],'Risk':[],'Optimization':[]}

markets = {'1':'GSPC','2':'FTSE','3':'NIKKEI','4':'BOVESPA','5':'CANADA',\
           '6':'AUSTRALIA','7':'Shanghai','8':'CRYPTO', '9':'Cedears','10':'MERVAL'}

def register_client():
    client_form['Names'].append(input('type the Name\n\n\t\t'))
    client_form['Emails'].append(input('Email to contact\n\n\t\t'))
    mercado = (input("Type the market to operate:\n(1) SP500,\n(2) FTSE,\n(3) NIKKEI,\n(4) BOVESPA,\
        \n(5) CANADA,\n(6) AUSTRALIA,\n(7) Shanghai,\n(8) CRYPTO,\n(9) Cedears,\n(10) MERVAL.\n\n\t\t"))
    client_form['Markets'].append(int(mercado)-1)
    client_form['Symbol'].append(markets[f"{mercado}"])
    client_form['Money'].append(input('How much to invest?\n\n\t\t'))                             
    risk = (input('(1) MinVar,\n(2) SharpeRatio,\n(3) SortinoRatio,\n(4) SharpeUnbound\n\n\t\t'))
    client_form['Optimization'].append(int(risk)-1)
    client_form['Risk'].append(risk.replace('1','MinVar').replace('2','SharpeRatio').replace('3','SortinoRatio').replace('4','SharpeBound'))
    return client_form
                             

def create():
    action = input("type + to add a client or else to exit\n\n\t\t")
    if action == '+':
        add = register_client()
        create()
    else:
        print('Finished clients registration')
    return client_form   

if __name__ == '__main__':
    create()
    client_form = pd.DataFrame(list(client_form.values()),index=list(client_form.keys())).T                   
    client_form.to_csv('new_clients.csv')
