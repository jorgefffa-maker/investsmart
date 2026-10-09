# InvestSmart — cotações diárias

Este pacote adiciona um fluxo para obter fechos diários de AAPL, MSFT, VOO e QQQ. Não altera automaticamente o teu `index.html`.

## 1. Criar a chave
Obtém uma chave gratuita em https://www.alphavantage.co/support/#api-key

## 2. Enviar ficheiros
Envia `fetch_quotes.py` e `.github/workflows/update-quotes.yml` para a raiz do repositório `investsmart`, mantendo a estrutura das pastas.

## 3. Guardar a chave como segredo
No repositório: Settings → Secrets and variables → Actions → New repository secret.
Name: `ALPHA_VANTAGE_API_KEY`
Secret: cola a chave. Não a coloques no HTML público.

## 4. Permitir ao fluxo guardar o ficheiro
Settings → Actions → General → Workflow permissions → “Read and write permissions” → Save.

## 5. Executar
Actions → “Atualizar cotações diárias” → Run workflow. Se ficar verde, deverá aparecer `data.json` na raiz. Se ficar vermelho, abre a execução para ler o erro.

## 6. Ligar o HTML a data.json
Faz primeiro uma cópia de segurança de `index.html`.
Encontra `const initial=[...];` e substitui o bloco `const initial` e a declaração `let assets=...` por:

```js
const initial=[
 {symbol:"AAPL",name:"Apple",category:"Ações",price:0,change:0,indicator:"A aguardar dados",kind:"wait"},
 {symbol:"MSFT",name:"Microsoft",category:"Ações",price:0,change:0,indicator:"A aguardar dados",kind:"wait"},
 {symbol:"VOO",name:"Vanguard S&P 500 ETF",category:"ETFs",price:0,change:0,indicator:"A aguardar dados",kind:"wait"},
 {symbol:"QQQ",name:"Invesco QQQ ETF",category:"ETFs",price:0,change:0,indicator:"A aguardar dados",kind:"wait"}
];
let assets=initial.map(x=>({...x})),cash=10000,positions={};
```

Depois, no fim do script, antes da chamada final `render();`, adiciona:

```js
async function carregarCotacoes(){
  const mensagem=document.getElementById("message");
  try{
    const resposta=await fetch("./data.json?ts="+Date.now(),{cache:"no-store"});
    if(!resposta.ok) throw new Error("HTTP "+resposta.status);
    const dados=await resposta.json();
    if(!dados.assets) throw new Error("O ficheiro não contém ativos.");
    for(const ativo of assets){
      const cotacao=dados.assets[ativo.symbol];
      if(cotacao && Number.isFinite(Number(cotacao.price))){
        ativo.price=Number(cotacao.price);
        ativo.change=Number(cotacao.change)||0;
        ativo.name=cotacao.name||ativo.name;
        ativo.indicator="Fecho diário";
        ativo.kind="wait";
      }
    }
    render();
    mensagem.textContent="Cotações diárias carregadas. Atualização do ficheiro: "+new Date(dados.updated_at).toLocaleString("pt-PT")+". Valores em USD; podem estar atrasados.";
  }catch(erro){
    mensagem.textContent="Não foi possível carregar cotações. Confirma se data.json existe e se o fluxo Actions terminou com sucesso. Detalhe: "+erro.message;
  }
}
```

Substitui a chamada final `render();` por:

```js
render();
carregarCotacoes();
```

Não deixes duplicadas as declarações `const initial` ou `let assets`. Faz commit e aguarda o Pages atualizar; depois abre o site e carrega Ctrl+F5.

## Limitações
São fechos diários, não preços em tempo real. O fornecedor pode não disponibilizar todos os símbolos em todos os planos e tem limites de utilização. Este protótipo não envia ordens nem é aconselhamento financeiro.
