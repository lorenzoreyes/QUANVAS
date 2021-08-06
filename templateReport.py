style = '''\
<!DOCTYPE html>
<html>
<head>
<style>
body {
  font-family: 'Trebuchet MS', sans-serif;
}

.header {
  width: 100%;
  padding: 1px;
  text-align: center;
  background-color: black;
  color: rgb(60, 179, 113);
  font-size: 42px;
}

tr:hover {background-color:rgb(0,0,0); color:rgb(60, 179, 113);}

/* Create two equal columns that sits next to each other */

table, th, td, tr {
  font-size: 12px;
  border: 1px solid black;
  padding: 1px;
  border-collapse: collapse;
  text-align: center;   
  white-space: nowrap;
  margin-left: auto; 
  margin-right: auto;
}
th {
  height: 16px;
}
</style>
</head>
<body>
'''
end_html =''' 
</body>
</html>'''


highlight = """<div class="header">
                <h1>QUANVAS</h1>
              </div> """

explanation = """\
        <h3>The current scenario in Argentina offers us 5 differents metrics in order to diagnose the stability of argentinian currency Peso.<br />Which are:\
          <ul>
                <li>Official Rate: given by the goverment.</li>
                <li>Official Solidarity Rate: it is a reference of the Official Rate plus taxes of 65%.</li>
                <li>Fundamental Forex: provided by dividing the liabilities of the Central Bank (BCRA) by the reserves.</li>
                <li>CCL AAPL.BA: convertion as a result of Apple US Stock divided by argentinian ADR (most representative as it holds 15% of Cedears volume).</li>
                <li>Monetary Vision: Official Rate plus the difference between the return of CCL AAPL.BA and the increase of Monetary Base.<br />As if Monetary Base and the Official Rate are perfectly correlated</li>
          </ul><br /></h3>"""

curve_futures = """<br /><h2>Time series and return from the current futures contracts available.</h2>"""


endWords = """<h3>Lessons and opportunities to keep an eye on:</h3>
             <h3><ul>
                <li>Eliminate uncertainty and risk.</li>
                <li>Forex Carry trade: going long in the spot and short on futures.</li>
                <li>Compare Solidarity Exchange Rate versus Apple Cedear for signals.</li>
              </ul></h3><br />
              <h2>STAY UPDATED OF THE MARKET</h2>"""  
