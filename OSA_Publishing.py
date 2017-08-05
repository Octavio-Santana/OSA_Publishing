# -*- coding: utf-8 -*-
"""
Created on Thu Aug  3 19:09:44 2017

Baixar informações gerais de todos os artigos no site osapublishing referente
ao tema "Goos-Hanchen shift

@author: octavio
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import pandas as pd
from bs4 import BeautifulSoup
import time

options = webdriver.ChromeOptions()
options.add_argument('headless')
#options.add_argument('window-size=1920x1080')

# Acessando a página inicial da osapublishing #

url = "https://www.osapublishing.org/"
driver = webdriver.Chrome(chrome_options=options)
#driver = webdriver.Chrome()
driver.get(url)

busc = raw_input("Digite o tema de pesquisa: ")
#busc = "Goos-Hanchen shift"

    # Aqui procuro pela caixa de busca
elem = driver.find_element_by_name("q")
    # Insiro busc na caixa de busca
elem.send_keys(busc)
elem.send_keys(Keys.RETURN)

#-----------------------------------------------------------------------------#
     # Determinar o número de páginas #
#-----------------------------------------------------------------------------#
def numb_page():
    time.sleep(20)
    count = ""
    result_count = driver.find_element_by_xpath("//span[@id='resultCount']").text
    for i in result_count:
        if i != " ":
            count += i
        else:
            break

    count = float(count)
    # Cada página tem o limite de 20 artigos #
    if int(count/20) == count/20:
        return int(count/20)
    else:
        return int(count/20)+1

##-----------------------------------------------------------------------------#
#    # Função Link: Notei que em alguns não tem link's para html e/ou pdf
##-----------------------------------------------------------------------------#
def Link(s, base_url):
    if len(s.findAll("a"))==3:
        # Se o tamanho é 3, então tem os link's (abstract, html e pdf) #
        return [
                base_url+s.findAll("a")[0].get("href"),
                base_url+s.findAll("a")[1].get("href"),
                base_url+s.findAll("a")[2].get("href")
                ]
    elif len(s.findAll("a"))==2:
        # Se o tamanho é 2, então tem os link's (abstract e pdf) #
        if s.findAll("a")[1].get_text() == 'PDF':
            return [
                    base_url+"/"+s.findAll("a")[0].get("href"),
                    None,
                    base_url+"/"+s.findAll("a")[1].get("href")
                    ]
    else:
        # Esse é o menos provavel de acontecer #
        return [
                    base_url+"/"+s.findAll("a")[0].get("href"),
                    None,
                    None
                    ]
#-----------------------------------------------------------------------------#
    # Percorre todas as páginas da busca #
#-----------------------------------------------------------------------------#
n_page = numb_page()
print "Número de páginas: %i" % n_page
n_page += 1

paper = []
base_url = "https://www.osapublishing.org"
all_page = driver.find_elements_by_xpath("//a[@data-value]")
#i = -1
#time.sleep(20)
for i in range(n_page):

    all_page[i].click()
    print "Página %i" % i
    time.sleep(5)    
    
    # Agora na nova página eu faço um soup da mesma para retirar as informações.
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    summary = soup.findAll("div",{"class":"sri-summary"})
        
    for summ in summary:
        s = summ.find("li",{"class":"sri-journal"}).get_text().replace("View: HTML | PDF","")
        s = s.replace("View: PDF","")  # Para os casos em que temos apenas Abstract e PDF
        s = s[1:len(s)-1] # Eliminar os espaços nas extremidades
        link = Link(summ, base_url)
        paper_entry = {
                        "Title": summ.find("h3",{"class":"sri-title"}).get_text(),
                        "Authors": summ.find("span",{"class":"sri-authors"}).get_text(),
                        "Year": summ.find("li",{"class":"sri-year"}).get_text(),
                        "Journal": s,
                        "Link Abstract": link[0],
                        "Link HTML": link[1],
                        "Link PDF": link[2]
                    }
        paper.append(paper_entry)
        
    all_page = driver.find_elements_by_xpath("//a[@data-value]")    

driver.close()
if len(paper) == 0:
    print "Nenhum artigo foi encontrado com o tema %s " % busc
    
else:    
    print "\n Acabou! \n"    
#-----------------------------------------------------------------------------#
    # Cirando um DataFrame #
#-----------------------------------------------------------------------------#
    df_paper = pd.DataFrame(paper, columns=["Title", "Authors", "Journal", "Year",
                                        "Link Abstract", "Link HTML", "Link PDF"])
#-----------------------------------------------------------------------------#
    # Salvando em um arquivo CSV
#-----------------------------------------------------------------------------#
    arq = raw_input("Nome do arquivo a ser salvo: ")
    df_paper.to_csv(arq+'.csv',encoding='utf-8')
