# Prompts

[English](../PROMPTS.md) | [README](../../README.pt-BR.md)

Como a IA foi usada para escrever esta extensão e como o resultado foi conferido. A regra: o modelo faz o rascunho, as fontes verificam, e os testes e o Revit decidem. Nenhuma chamada da API do Revit é aceita até ser encontrada na documentação da Autodesk ou em código real do pyRevit.

## Modelo de prompt para código da API do Revit

```text
Contexto: extensão do pyRevit no mecanismo IronPython 2.7 (janelas WPF não são compatíveis com o CPython),
Revit <versão>. O código também deve rodar no CPython 3 nos testes: sem f-strings, sem anotações de tipo,
literais u"" para texto com acentos.
Objetivo: <um botão, uma frase>.
Entradas: <seleção ou modelo inteiro>. Saída: <janela, gravação de parâmetro ou CSV>.
Restrições: lógica pura em lib/bauser_core.py, sem importações do Revit. Chamadas do Revit só em
lib/bauser_revit.py. Gravações em uma transação. Os comprimentos do Revit estão em pés, converta para metros.
Peça: liste todo membro da API do Revit que você usar, com a sua classe, para que cada um possa ser conferido.
Não invente membros. Se não tiver certeza, escreva "não verificado".
```

## Lista de verificação para cada chamada do Revit

1. Encontre o membro na documentação da API da Autodesk e anote a sua classe e a sua assinatura.
2. Encontre o mesmo idioma de uso em código real do pyRevit, como a ferramenta ReNumber e as ferramentas de parede do repositório do pyRevit.
3. Ponha a lógica no módulo puro e cubra-a em `tests/test_core.py`.
4. Rode o adaptador e os scripts reais contra o Revit simulado em `tests/test_adapter.py`.
5. Quebre o código de propósito e confirme que um teste falha. Um teste que não pode falhar não verifica nada.
6. Rode o botão no Revit em um modelo pequeno com respostas contadas à mão.

## Exemplos trabalhados

| Funcionalidade | Conferido contra | O que a conferência mudou |
|---|---|---|
| Contar painéis | Uso de `FilteredElementCollector` no pyRevit, parâmetro `HOST_AREA_COMPUTED`[^area] | A Área da parede já é líquida de aberturas, o que levou às opções de área líquida e de tamanho total do painel |
| Numerar painéis | O ReNumber do pyRevit, que usa `ALL_MODEL_MARK` e `Parameter.Set`[^renumber] | O mesmo parâmetro, mais uma caixa de confirmação e uma nota sobre desfazer |
| Coluna Aberturas | `HostObject.FindInserts` da Autodesk, herdado por `Wall`[^findinserts] | A chamada foi adicionada depois que a assinatura foi confirmada |
| Tamanho total do painel | Uma ferramenta de parede do pyRevit usa `get_BoundingBox(None)` com `Min.Z` e `Max.Z`[^wallbbox]; a Autodesk define a caixa como a que circunscreve toda a geometria[^bbox] | A altura vem da caixa delimitadora, e não da Altura desconectada |
| Paredes irregulares | `Wall.SketchId` e `Wall.CrossSection` da Autodesk[^wall] | Um aviso para paredes em que comprimento vezes altura superestima o painel |
| Janela de resultados | `WPFWindow` e `FindName` do pyRevit, e o módulo de formulários do CPython[^pyrevit] | O WPF não é compatível com o CPython, e por isso a extensão precisa usar o IronPython |
| Texto com acentos | Regras de strings do IronPython 2.7 | Todo literal com acento virou `u""` |
| Código de classificação | Os nomes de parâmetros da API do Revit[^rename] e uma resposta da comunidade sobre famílias de sistema[^community] | Os primeiros resultados da busca mostraram só os nomes antigos dos parâmetros. Ao ler mais, apareceu a mudança de nome na API do Revit 2026 e um tópico dizendo que as paredes não têm Classification Number, e por isso o adaptador tenta os dois nomes e usa o Código de montagem como alternativa |
| Nomes de parâmetros no IDS | A ajuda da Autodesk em português, que mostra nomes de parâmetros traduzidos[^ptb] | Um Revit em português não encontraria `FireRating`, e por isso a configuração ganhou uma tabela de apelidos |
| Títulos da faixa de opções | A tabela de idiomas do pyRevit e os seus próprios arquivos `bundle.yaml`[^locales] | Títulos e dicas são dados para `en_us` e `pt_br` e seguem o idioma do Revit |
| Verificação IDS | O esquema IDS 1.0 publicado e os seus casos de teste[^idsschema] | O leitor segue os nomes de elementos e os valores de cardinalidade reais. O arquivo de exemplo foi validado contra a estrutura do esquema |

## Notas

Um primeiro rascunho escrito de memória parecia certo e continuava não verificado. Ler o código-fonte do pyRevit encontrou o limite do CPython antes que ele pudesse falhar diante de um usuário. Pedir ao modelo que liste os membros da API que usou dá a lista de verificação acima. Os preços, as perdas e a cotação são valores provisórios até que uma fonte real os forneça, e a janela diz isso.

Duas verificações têm limites que vale declarar. O exemplo de IDS foi validado contra o esquema com as referências aos tipos nativos do XML Schema afrouxadas, porque o validador não conseguiu resolvê-las sozinho, e por isso a verificação cobre a estrutura e não a sintaxe das restrições. E o Revit simulado em `tests/test_adapter.py` mostra que as chamadas têm o formato certo, e não que o Revit se comporta do mesmo modo.

[^area]: TAMMIK, Jeremy. Calculating Gross and Net Wall Areas. The Building Coder. [S. l.], [20--]. Disponível em: https://jeremytammik.github.io/tbc/a/1296_spatial_calculator.htm. Acesso em: 20 out. 2026. Citado pela afirmação de que o parâmetro de área da parede tem as aberturas hospedadas descontadas.
[^renumber]: PYREVIT PROJECT. extensions/pyRevitTools.extension/pyRevit.tab/Modify.panel/edit2.stack/ReNumber.pushbutton/script.py. [S. l.]: pyRevit Labs, [20--]. Disponível em: https://github.com/pyrevitlabs/pyRevit. Acesso em: 20 out. 2026. Citado porque lê e grava o parâmetro Marca por `ALL_MODEL_MARK` dentro de uma transação, que é o idioma de uso que o botão Numerar painéis segue.
[^findinserts]: AUTODESK. HostObject.FindInserts Method. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/58990230-38cb-3af7-fd25-96ed3215a43d.htm. Acesso em: 20 out. 2026. Citado pela assinatura e pelos quatro indicadores.
[^wallbbox]: PYREVIT PROJECT. extensions/pyRevitTools.extension/pyRevit.tab/Drawing Set.panel/views.stack/Views.pulldown/Create Parallel Section.pushbutton/script.py. [S. l.]: pyRevit Labs, [20--]. Disponível em: https://github.com/pyrevitlabs/pyRevit. Acesso em: 20 out. 2026. Citado porque lê `wall.get_BoundingBox(None)` e usa `Min.Z` e `Max.Z`, que é a chamada que esta extensão usa para a altura de uma parede.
[^bbox]: AUTODESK. Element.BoundingBox Property. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/def2f9f2-b23a-bcea-43a3-e6de41b014c8.htm. Acesso em: 20 out. 2026. Citado pela definição da caixa delimitadora como a que circunscreve toda a geometria do elemento.
[^wall]: AUTODESK. Wall Class. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/b5891733-c602-12df-beab-da414b58d608.htm. Acesso em: 20 out. 2026. Citado pelas propriedades `SketchId` e `CrossSection`.
[^pyrevit]: PYREVIT PROJECT. pyrevitlib/pyrevit/forms/_cpy.py e _ipy.py. [S. l.]: pyRevit Labs, [20--]. Disponível em: https://github.com/pyrevitlabs/pyRevit. Acesso em: 20 out. 2026. Citado porque o módulo do CPython marca `WPFWindow` como não compatível e o do IronPython o implementa.
[^rename]: REVITAPIDOCS.COM. API Changes 2026. [S. l.]: revitapidocs.com, 2026. Disponível em: https://www.revitapidocs.com/2026/news. Acesso em: 20 out. 2026. Citado pela mudança na API do Revit 2026 que renomeou `OMNICLASS_CODE` para `CLASSIFICATION_CODE` e `UNIFORMAT_CODE` para `ASSEMBLY_CODE`. O site é um espelho de terceiros da lista de mudanças da Autodesk. Os nomes antigos estão na listagem da enumeração de 2025 em https://www.revitapidocs.com/2025/fb011c91-be7e-f737-28c7-3f1e1917a0e0.htm.
[^community]: CLASSIFICATION Number (Omniclass) NOT working Revit 2026. Autodesk Community, 12 maio 2026. Disponível em: https://forums.autodesk.com/t5/revit-architecture-forum/classification-number-omniclass-not-working-revit-2026/td-p/14126346. Acesso em: 20 out. 2026. Citado por uma resposta que diz que a classificação não existe para famílias de sistema. É a declaração de um usuário, e não a documentação da Autodesk.
[^ptb]: AUTODESK. Propriedades de tipo de paredes. In: AUTODESK. Ajuda do Revit 2012. Português (Brasil). [S. l.]: Autodesk, 2012. Disponível em: https://help.autodesk.com/view/RVT/2012/PTB/caas.html?url=caas%2Fvhelp%2Fhelp-dev-autodesk-com%2Fv%2FRevit%2Fptb%2F2012%2FHelp%2F0000-Guia-do-01%2F0325-Construi325%2F0327-Modelage327%2F0328-Paredes328%2F0332-Modifica332%2F0380-Propried380.html. Acesso em: 20 out. 2026. Citado porque mostra que nomes de parâmetros como Código de montagem são traduzidos na interface em português.
[^locales]: PYREVIT PROJECT. pyrevitlib/pyrevit/coreutils/applocales.py e os arquivos de bundle de extensions/pyRevitTools.extension. [S. l.]: pyRevit Labs, [20--]. Disponível em: https://github.com/pyrevitlabs/pyRevit. Acesso em: 20 out. 2026. Citado pelo código de idioma `pt_br` e pelo formato de `title` e `tooltip` em `bundle.yaml`.
[^idsschema]: BUILDINGSMART. Repositório do IDS: Schema/ids.xsd e os casos de teste em Documentation/ImplementersDocumentation/TestCases. [S. l.]: buildingSMART International, [20--]. Disponível em: https://github.com/buildingSMART/IDS. Acesso em: 20 out. 2026. Citado porque o leitor e os seus testes seguem os nomes de elementos, os valores de cardinalidade e os arquivos de exemplo desse repositório.
