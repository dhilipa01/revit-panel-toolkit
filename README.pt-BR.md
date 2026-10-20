<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/media/wordmark-dark.svg">
  <img src="docs/media/wordmark-light.svg" alt="revit-panel-toolkit" width="640">
</picture>

Calcule a quantidade e o preço de painéis de parede pela faixa de opções do Revit.

Uma extensão do pyRevit para construção painelizada e industrializada.

[![CI](https://img.shields.io/github/actions/workflow/status/dhilipa01/revit-panel-toolkit/ci.yml?branch=main&style=flat-square&label=CI&labelColor=14213D&color=3A4A66)](https://github.com/dhilipa01/revit-panel-toolkit/actions/workflows/ci.yml)
[![Licença](https://img.shields.io/badge/licen%C3%A7a-MIT-3A4A66?style=flat-square&labelColor=14213D)](LICENSE)
[![pyRevit](https://img.shields.io/badge/pyRevit-IronPython-3A4A66?style=flat-square&labelColor=14213D)](https://github.com/pyrevitlabs/pyRevit)

[Documentation in English](README.md)

</div>

```text
$ python examples/panel_budget.py --lang pt
Marca  Tipo                 Nível    Aberturas    Área m²  Preço R$/m²   Custo R$
P-001  Painel de fachada    Nível 1          1       6,60       520,00   3.432,00
P-002  Painel de fachada    Nível 1          0       8,40       520,00   4.368,00
P-003  Painel de divisória  Nível 1          1       4,82       310,00   1.494,20
P-004  Painel de fachada    Nível 2          1       6,60       520,00   3.432,00

Base         área líquida
Total        R$ 13.362,51  (com 5% de perdas)
Aprox.       € 2.357,45  (EUR/BRL 5,6682, 2026-10-19)
```

O exemplo roda sem o Revit, com painéis inventados e preços ilustrativos.

> Status: a lógica é coberta por testes que rodam fora do Revit. A extensão ainda não foi executada em uma sessão real do Revit. Veja [Verificar no Revit](docs/pt-BR/VERIFICAR_NO_REVIT.md).

## Documentação em inglês

Esta página é a versão em português do [README em inglês](README.md). As duas versões têm o mesmo conteúdo, e a documentação completa está nos dois idiomas. Os títulos e as dicas dos botões na faixa de opções também estão traduzidos e seguem o idioma do Revit.

## Por quê

A painelização leva para a fábrica a produção de painéis pré-fabricados de fachada e de paredes internas. Cada painel precisa de uma quantidade, de um número e de um preço antes de entrar em produção, e as equipes costumam tirar esses dados à mão das tabelas de quantidades do Revit. Esta extensão lê os dados do modelo, com um botão da faixa de opções para cada etapa. Ela é uma pequena parte de um fluxo de projeto entre o modelo BIM e a fábrica, e a estimativa de custo também dá uma visão antecipada da viabilidade.

Clientes públicos brasileiros também pedem um código de classificação nos elementos do modelo e uma lista verificável das informações exigidas.[^nbr15965] Os botões Classificar painéis e Verificar IDS atendem a esses dois pedidos sem prender a extensão à configuração de uma empresa específica.

## Funcionalidades

- Conta os painéis por tipo de parede, com quantidade, aberturas e área.
- Numera os painéis em uma única transação desfazível, primeiro por nível e depois da esquerda para a direita.
- Calcula o preço dos painéis pela área líquida ou pelo tamanho total do painel, com um fator de perdas.
- Grava um código de classificação, como um código da NBR 15965, em cada tipo de parede.[^classify]
- Verifica os painéis contra um arquivo de Especificação de Entrega de Informação (IDS, na sigla em inglês) do buildingSMART.[^ids]
- Mostra o valor em reais com um valor aproximado em euros.
- Exporta um CSV por painel e um CSV de orçamento com código, descrição, unidade, quantidade, preço unitário e total.
- Alterna os rótulos entre português e inglês pela faixa de opções e mostra a faixa de opções no idioma do Revit.
- Mantém a lógica em Python simples, de modo que ela roda e é testada fora do Revit.

## Instalação

Requer o Revit com o pyRevit, no mecanismo IronPython padrão. As janelas WPF do pyRevit não são compatíveis com o mecanismo CPython.[^pyrevit]

```bash
git clone https://github.com/dhilipa01/revit-panel-toolkit.git
```

1. No Revit, abra a guia pyRevit e escolha Configurações.
2. Em Diretórios de extensões personalizadas, adicione a pasta `src` do clone.
3. Escolha Salvar configurações e recarregar.

A extensão adiciona uma guia à faixa de opções, com seis botões.

## Uso

Selecione algumas paredes, ou não selecione nada para usar todas as paredes do modelo, e clique em um botão.

| Botão | O que faz | Altera o modelo |
|---|---|---|
| Contar painéis | Lista os tipos de parede com quantidade, aberturas e área | Não |
| Numerar painéis | Grava `P-001`, `P-002` e assim por diante no parâmetro Marca, por nível e depois por X | Sim, em uma transação desfazível |
| Custo dos painéis | Pergunta a base de preço e o fator de perdas e mostra o custo em reais e o valor aproximado em euros | Não |
| Classificar painéis | Grava o código de classificação definido para cada tipo de parede em `bauser_config.json`, em Classification Number ou em Código de montagem | Sim, nos tipos de parede, em uma transação desfazível |
| Verificar IDS | Pede um arquivo `.ids` e lista, para cada painel, os requisitos que ele atende ou não atende | Não |
| PT / EN | Alterna os rótulos entre português e inglês | Não |

Os painéis são paredes do Revit. A área líquida é o parâmetro Área da parede, que já desconta as aberturas.[^area] O tamanho total do painel é o comprimento vezes a altura, com as aberturas incluídas. A área líquida é a base padrão. A contagem de aberturas vem de `HostObject.FindInserts`.[^findinserts] A referência completa está em [docs/pt-BR/REFERENCIA.md](docs/pt-BR/REFERENCIA.md).

## Exemplos

Rode o exemplo sem o Revit e sem dependências:

```bash
python examples/panel_budget.py                      # área líquida, em inglês
python examples/panel_budget.py --gross              # tamanho total do painel
python examples/panel_budget.py --lang pt budget.csv # rótulos e formato em português, e grava o CSV de orçamento
python examples/panel_budget.py --help
```

O CSV de orçamento, em formato brasileiro:

```text
Código;Descrição;Un.;Qtd.;Preço unit. (R$);Total (R$)
;Painel de divisória;m2;4,82;310,00;1.494,20
;Painel de fachada;m2;21,60;520,00;11.232,00
;Perdas (5%);;;;636,31
;TOTAL (R$);;;;13.362,51
;TOTAL (EUR, aprox.);;;;2.357,45
```

Defina um preço, uma referência do SINAPI e um código de classificação para um tipo de parede em `src/Bauser.extension/bauser_config.json`:

```json
{
  "rates": {
    "Fachada": {
      "rate": 520.0,
      "sinapi": "",
      "classification": { "system": "NBR 15965", "code": "3E.02" }
    }
  },
  "ids_aliases": { "FireRating": ["Classificação de resistência ao fogo"] }
}
```

Um tipo de parede cujo nome contém "Fachada" passa a ter o preço de R$ 520,00/m² e recebe o código `3E.02` quando você clica em Classificar painéis. O código é um exemplo, não um código verificado. A referência do SINAPI é apenas um rótulo.[^sinapi] O apelido permite que um Revit que mostra os nomes dos parâmetros traduzidos atenda a uma propriedade IDS chamada `FireRating`. O nome em português do exemplo é ilustrativo, e o nome correto é o que o seu Revit mostra.

O arquivo `examples/panel_requirements.ids` é um exemplo de arquivo IDS. Ele exige que toda parede tenha uma Marca, uma classificação no sistema NBR 15965 e uma resistência ao fogo. Clique em Verificar IDS, escolha o arquivo, e a janela lista cada painel contra cada requisito.

## Configuração

Todas as configurações estão em `src/Bauser.extension/bauser_config.json`. Todas as chaves são opcionais, e um erro no arquivo gera uma mensagem que indica a chave.

| Chave | Padrão | Significado |
|---|---|---|
| `default_rate` | `490.0` | Preço provisório em R$/m² para os tipos de parede sem entrada em `rates` |
| `waste` | `0.05` | Fator de perdas padrão |
| `mark_prefix` | `"P-"` | Prefixo dos valores de Marca |
| `fx` | EUR/BRL 5,6682, 2026-10-19 | Cotação de fechamento do serviço PTAX do Banco Central do Brasil, atualizada à mão[^ptax] |
| `rates` | `{}` | Para cada parte do nome do tipo de parede: `rate`, uma `sinapi` opcional e uma `classification` opcional com `system` e `code` |
| `ids_aliases` | `{}` | Para cada nome de propriedade IDS, uma lista de nomes de parâmetros do Revit que a atendem |

Recarregue o pyRevit depois de editar o arquivo. O idioma das janelas fica na configuração do pyRevit e muda com o botão PT / EN. Os preços e as perdas deste repositório são valores de demonstração. Os valores numéricos do arquivo usam o ponto decimal, porque o formato é JSON.

## Convenções desta documentação

- A ortografia segue o Acordo Ortográfico da Língua Portuguesa de 1990, promulgado no Brasil pelo Decreto nº 6.583/2008.[^acordo]
- As notas de rodapé são numeradas na ordem da primeira aparição e trazem os elementos que a ABNT NBR 6023:2025 pede em uma referência: a entidade responsável, o título, o endereço e a data de acesso.[^nbr6023] Cada nota diz também por que a fonte foi citada.
- Os números usam a vírgula decimal e o ponto como separador de milhares. As datas aparecem por extenso ou no formato ano-mês-dia nas saídas dos programas.
- Os termos do Revit seguem a ajuda da Autodesk em português do Brasil quando ela traz o termo.[^ptbhelp] Quando não traz, o nome em inglês aparece em fonte de código, e a tabela de termos em [docs/pt-BR/REFERENCIA.md](docs/pt-BR/REFERENCIA.md) indica o que foi e o que não foi confirmado.
- Nenhuma norma da ABNT define o formato de um README. A norma de trabalhos acadêmicos (ABNT NBR 14724) e a numeração progressiva de seções (ABNT NBR 6024) não são seguidas, porque foram escritas para outro tipo de documento. Veja [docs/pt-BR/NORMAS_E_FONTES.md](docs/pt-BR/NORMAS_E_FONTES.md).

## Documentação

- [Referência](docs/pt-BR/REFERENCIA.md): botões, parâmetros do Revit, fórmulas, formatos de CSV, a verificação IDS, funções dos módulos e termos do Revit
- [Normas e fontes](docs/pt-BR/NORMAS_E_FONTES.md): ABNT NBR 16970, NBR 15965, IDS, SINAPI, os decretos de BIM, UE-Mercosul, cotações e normas brasileiras de documentação
- [Roteiro](docs/pt-BR/ROTEIRO.md)
- [Verificar no Revit](docs/pt-BR/VERIFICAR_NO_REVIT.md)
- [Prompts](docs/pt-BR/PROMPTS.md): como a IA foi usada e como o resultado foi conferido
- [Registro de alterações](CHANGELOG.md), em inglês
- [Documentation in English](README.md)

## Desenvolvimento

```bash
python tests/test_core.py      # preços, numeração, formatos, configuração, CSV
python tests/test_ids.py       # o leitor e o verificador IDS
python tests/test_adapter.py   # o adaptador e os scripts reais contra um pequeno simulador do pyRevit e da API do Revit
pip install ruff && ruff check .
```

```text
src/Bauser.extension/   a extensão do pyRevit: guia, botões, lib, bauser_config.json
tests/                  testes que rodam sem o Revit
examples/               exemplo executável e um arquivo IDS de exemplo
docs/                   referência, normas, roteiro, listas de verificação
docs/pt-BR/             a mesma documentação em português do Brasil
```

O código roda no IronPython 2.7 e no CPython 3. Ele não usa f-strings nem anotações de tipo, e o texto com acentos usa literais `u""`. Uma tag como `v0.3.0` aciona o fluxo de publicação, que testa o código e anexa um arquivo zip da extensão.

## Como contribuir

Abra uma issue antes de uma alteração grande e rode os três arquivos de teste e `ruff check .` antes de um pull request. Comece as mensagens de commit com `feat:`, `fix:`, `docs:` ou `refactor:`. As alterações na documentação devem ser feitas nos dois idiomas.

## Licença

MIT. Veja [LICENSE](LICENSE).

[^nbr15965]: DNIT. Caderno de Requisitos Técnicos BIM. [S. l.]: DNIT, 2023. Disponível em: https://www.gov.br/dnit/pt-br/assuntos/planejamento-e-pesquisa/bim-no-dnit/mosaico-de-servicos/documentos-tecnicos-bim/CRTBIM__2023_v2.pdf. Acesso em: 20 out. 2026. Citado porque é um documento de cliente federal que indica a ABNT NBR 15965 como sistema de classificação da informação do modelo e pede um Plano de Execução BIM que fixe a codificação. O caderno do Governo de Santa Catarina (https://www.sie.sc.gov.br/webdocs/sie/doc-tecnicos/labim/Caderno%20de%20Especifica%C3%A7%C3%B5es%20de%20Projetos%20em%20BIM_102018.pdf) vai além e exige ao menos um sistema de classificação nos parâmetros do modelo.
[^classify]: AUTODESK. Parameter.Set(String) Method. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/956a1e23-cfe5-a60b-1ff9-0e8e33812774.htm. Acesso em: 20 out. 2026. Citado porque informa que a chamada falha quando o parâmetro é somente leitura, o que explica por que o botão relata o parâmetro somente leitura em vez de forçar a gravação. A mudança de nome do parâmetro de classificação na API do Revit 2026 consta em https://www.revitapidocs.com/2026/news, um site de terceiros que reproduz a lista de mudanças da Autodesk. Uma resposta na Comunidade Autodesk diz que o Classification Number não existe para famílias de sistema, como as paredes (https://forums.autodesk.com/t5/revit-architecture-forum/classification-number-omniclass-not-working-revit-2026/td-p/14126346). Essa é a declaração de um usuário, e não da Autodesk, e por isso o botão usa o Código de montagem como alternativa. Ainda não foi confirmado no Revit se algum dos dois parâmetros aceita um código qualquer.
[^ids]: BUILDINGSMART INTERNATIONAL. What is Information Delivery Specification (IDS). [S. l.]: buildingSMART International, 2023. Disponível em: https://www.buildingsmart.org/what-is-information-delivery-specification-ids. Acesso em: 20 out. 2026. Citado porque define o IDS como uma descrição legível por máquina da informação que um modelo deve entregar, que é o que o botão Verificar IDS lê. A estrutura do arquivo usada pelo leitor é o esquema 1.0 publicado: https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd.
[^pyrevit]: PYREVIT PROJECT. Arquivos pyrevitlib/pyrevit/forms/_cpy.py e _ipy.py. [S. l.]: pyRevit Labs, [20--]. Disponível em: https://github.com/pyrevitlabs/pyRevit. Acesso em: 20 out. 2026. Citado porque o módulo de formulários do CPython marca `WPFWindow` como não compatível e o do IronPython o implementa, e por isso esta extensão precisa usar o mecanismo IronPython.
[^area]: TAMMIK, Jeremy. Calculating Gross and Net Wall Areas. The Building Coder. [S. l.], [20--]. Disponível em: https://jeremytammik.github.io/tbc/a/1296_spatial_calculator.htm. Acesso em: 20 out. 2026. Citado porque afirma que o parâmetro de área da parede já tem as aberturas descontadas, e por isso pode servir como valor líquido. O suporte da Autodesk acrescenta que a área das aberturas não pode ser lida diretamente como parâmetro: https://www.autodesk.com/support/technical/article/caas/sfdcarticles/sfdcarticles/How-to-create-parameter-that-extract-the-area-of-openings-in-the-walls-in-Revit.html.
[^findinserts]: AUTODESK. HostObject.FindInserts Method. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/58990230-38cb-3af7-fd25-96ed3215a43d.htm. Acesso em: 20 out. 2026. Citado pela assinatura e pelo valor de retorno da chamada que lista as portas, as janelas e as aberturas retangulares de uma parede. A classe `Wall` a herda de `HostObject`.
[^sinapi]: CAIXA ECONÔMICA FEDERAL. SINAPI. [S. l.]: Caixa, [20--]. Disponível em: https://www.caixa.gov.br/poder-publico/modernizacao-gestao/sinapi/Paginas/default.aspx. Acesso em: 20 out. 2026. Citado porque o SINAPI é a referência mensal de custos da qual partem os orçamentos de obras pagas com recursos federais, e por isso uma linha de orçamento precisa de um lugar para o código da composição. Nada é importado do SINAPI.
[^ptax]: BANCO CENTRAL DO BRASIL. Serviço de cotações PTAX. [S. l.]: BCB, [20--]. Disponível em: https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata/. Acesso em: 20 out. 2026. Citado como a fonte da cotação de fechamento EUR/BRL de 2026-10-19. O serviço não exige chave e lista dez moedas, entre as quais não estão ARS, UYU e PYG.
[^acordo]: BRASIL. Decreto nº 6.583, de 29 de setembro de 2008. Promulga o Acordo Ortográfico da Língua Portuguesa, assinado em Lisboa, em 16 de dezembro de 1990. Diário Oficial da União, Brasília, 30 set. 2008. Disponível em: http://presidencia.gov.br/ccivil_03/_ato2007-2010/2008/decreto/d6583.htm. Acesso em: 20 out. 2026. Citado porque é o ato que promulga o acordo ortográfico que esta documentação segue.
[^nbr6023]: ASSOCIAÇÃO BRASILEIRA DE NORMAS TÉCNICAS. ABNT NBR 6023:2025: informação e documentação: referências: elaboração. 3. ed. Rio de Janeiro: ABNT, 2025. Disponível em: https://estatico.tre-rn.jus.br/ABNT_NBR_6023_2025.pdf. Acesso em: 20 out. 2026. Citado porque cancela e substitui a edição de 2018 e porque admite a referência em nota de rodapé. A cópia consultada é uma cópia licenciada, publicada por um órgão público, e só esses dois pontos foram usados.
[^ptbhelp]: AUTODESK. Paleta Propriedades. In: AUTODESK. Ajuda do Revit 2026. Português (Brasil). [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/view/RVT/2026/PTB/?guid=GUID-A764EA7A-FE26-469B-857C-F3A70812FC34. Acesso em: 20 out. 2026. Citado como a redação da própria Autodesk para a paleta Propriedades, as propriedades de instância e de tipo, a Altura desconectada e a faixa de opções. A página sobre as partes da interface está em https://help.autodesk.com/view/RVT/2026/PTB/?guid=GUID-7793667D-5657-4382-9BEC-F7CB6AC8F53E.
