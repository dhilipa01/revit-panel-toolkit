# Referência

[English](../REFERENCE.md) | [README](../../README.pt-BR.md)

## Botões da faixa de opções

Os seis botões ficam em um único painel da faixa de opções, chamado Panels, na guia da extensão.

| Botão | Lê | Grava | Resultado |
|---|---|---|---|
| Contar painéis | Paredes: tipo de parede, Área, caixa delimitadora, inserções | Nada | Janela com uma tabela por tipo de parede e exportação em CSV |
| Numerar painéis | Paredes: Nível, localização, tipo de parede, Área | Marca (parâmetro de instância), em uma transação | Janela com a lista numerada e exportação em CSV |
| Custo dos painéis | Paredes, como acima | Nada | Janela com uma tabela por painel, CSV por painel e CSV de orçamento |
| Classificar painéis | Tipos de parede e `bauser_config.json` | O parâmetro de classificação de cada tipo de parede (Classification Number ou, se o tipo não tiver, Código de montagem), em uma transação | Janela com uma linha por tipo de parede, o parâmetro gravado e exportação em CSV |
| Verificar IDS | Paredes com todos os seus parâmetros e um arquivo `.ids` | Nada | Janela com uma linha por painel e requisito e exportação em CSV |
| PT / EN | Configuração do pyRevit | Configuração do pyRevit | Caixa de diálogo |

Escopo: as paredes da seleção atual. Sem seleção, todas as paredes do modelo.

## Dados do Revit usados

| Valor | Fonte |
|---|---|
| Área líquida | Parâmetro interno `HOST_AREA_COMPUTED` (Área). O Revit desconta as aberturas hospedadas[^area] |
| Comprimento | Parâmetro interno `CURVE_ELEM_LENGTH` (Comprimento) |
| Altura | `Element.get_BoundingBox(None)`: Max.Z menos Min.Z. Usa a Altura desconectada (`WALL_USER_HEIGHT_PARAM`) se não houver caixa[^bbox] |
| Tamanho total do painel | Comprimento vezes altura, convertido em m² |
| Aberturas | `HostObject.FindInserts(True, False, False, False)`: portas, janelas e aberturas retangulares da parede[^findinserts] |
| Nível e cota | O nível da Restrição da base da parede e sua propriedade `Elevation` |
| Marca | Parâmetro interno `ALL_MODEL_MARK` |
| Parede irregular | `Wall.SketchId` (perfil editado, Revit 2022 e posteriores) ou `Wall.CrossSection` diferente de vertical[^wall] |
| Código de classificação | Parâmetro de tipo `CLASSIFICATION_CODE` (Classification Number), `OMNICLASS_CODE` (OmniClass Number) antes da API do Revit 2026, e depois `ASSEMBLY_CODE` ou `UNIFORMAT_CODE` (Código de montagem) como alternativa[^classparam] |
| Todos os parâmetros | Cada parâmetro da parede e do seu tipo, pelo nome, para a verificação IDS |

O Revit guarda os comprimentos em pés. O adaptador converte para metros e metros quadrados.

## Cálculo de preço

```text
custo por painel = área x preço
total            = soma dos custos dos painéis x (1 + perdas)
por m²           = total / soma das áreas
EUR              = total / cotação EUR/BRL
```

A área líquida é a base padrão. A opção de tamanho total do painel usa comprimento vezes altura. Para paredes com perfil editado ou com seção inclinada ou cônica, o tamanho total do painel é um limite superior, e o botão Custo dos painéis avisa sobre elas. As paredes com topo ou base anexados a outro elemento não são detectadas.

## Numeração

Os painéis são ordenados pela cota do nível, depois por X, depois por Y e depois pelo identificador do elemento. As marcas são o prefixo de marca seguido de um contador de três dígitos, por exemplo `P-001`. Os parâmetros de Marca somente leitura são ignorados e contados.

## Classificação

O botão Classificar painéis olha o nome do tipo de parede de cada painel. Para cada entrada configurada cujo trecho de nome aparece no nome do tipo, ele grava o código no parâmetro de classificação do tipo. Os tipos sem código configurado não são alterados e são contados. A alteração vale para o tipo de parede, de modo que todas as paredes desse tipo recebem o código, e Ctrl+Z a desfaz.

O código vai para o primeiro parâmetro gravável, nesta ordem: Classification Number (`CLASSIFICATION_CODE`, ou `OMNICLASS_CODE` antes da API do Revit 2026) e, depois, Código de montagem (`ASSEMBLY_CODE`, ou `UNIFORMAT_CODE` antes da API do Revit 2026).[^classparam] A tabela de resultados mostra o nome do parâmetro gravado.

A alternativa existe porque as paredes são uma família de sistema, e uma resposta na Comunidade Autodesk diz que o Classification Number não existe para famílias de sistema.[^community] O Código de montagem existe nos tipos de parede, mas é o parâmetro de um código Uniformat escolhido em uma lista, e por isso um código da NBR 15965 nele é uma solução de compromisso.[^assembly] Um parâmetro somente leitura é relatado como Somente leitura e não é forçado, porque `Parameter.Set` falha nele.[^setstring]

Três pontos não foram confirmados e dependem de uma sessão real do Revit: se o Classification Number aparece em um tipo de parede, se algum dos dois parâmetros aceita um código que não esteja no arquivo de classificação do próprio Revit, e quais versões do Revit se comportam de cada modo. Veja [Verificar no Revit](VERIFICAR_NO_REVIT.md).

## Verificação IDS

O botão Verificar IDS lê um arquivo IDS 1.0 do buildingSMART[^ids] e testa os painéis contra ele. A verificação usa os parâmetros do Revit, e não um arquivo IFC. Um modelo exportado para IFC ainda deve ser validado com uma ferramenta de IFC.

| Termo do IDS | O que a verificação faz |
|---|---|
| Entidade `IFCWALL`, `IFCWALLSTANDARDCASE` | Todo painel é uma parede. Uma especificação para outra entidade não corresponde a nenhum painel |
| Propriedade | Procura um parâmetro do Revit na parede ou no seu tipo com o mesmo nome. Maiúsculas, espaços e sublinhados são ignorados, de modo que `FireRating` corresponde a Fire Rating. O conjunto de propriedades não é verificado. Um valor vazio conta como ausente |
| Classificação | Compara o código do parâmetro de classificação do tipo e o sistema indicado para esse tipo de parede em `bauser_config.json` |
| Atributo | `Name` é o nome do tipo de parede, `Tag` é a Marca e `Description` é o parâmetro Descrição. Os outros atributos aparecem como Não verificado |
| Cardinalidade | `required`, `optional` e `prohibited` são tratados nos requisitos |
| Valores | Um valor simples, uma enumeração ou um padrão. O padrão deve corresponder ao valor inteiro, como no XML Schema |

O Revit traduz os nomes dos seus parâmetros internos. Em um Revit em português, um parâmetro como Fire Rating aparece com um nome em português, e uma propriedade chamada `FireRating` no arquivo IDS não seria encontrada. A chave `ids_aliases` de `bauser_config.json` lista, para cada nome de propriedade do IDS, os nomes de parâmetros do Revit que a atendem. A ajuda da Autodesk em português do Brasil confirma que a interface é traduzida, por exemplo Código de montagem para Assembly Code.[^ptb] O nome em português que o Revit mostra para cada parâmetro precisa ser lido no modelo.

Todo o resto gera uma linha Não verificado, e nunca uma aprovação silenciosa: as outras restrições de valor, as facetas `partOf` e `material` e as aplicabilidades que as usam. Cada linha de resultado tem o painel, a especificação, o requisito, o resultado e um detalhe curto.

## Formatos de CSV

Todas as exportações são UTF-8 com marca de ordem de bytes. O português usa `;` como delimitador e a vírgula decimal. O inglês usa `,` e o ponto decimal.

| Arquivo | Colunas |
|---|---|
| Exportação por painel | As colunas da tabela da janela |
| Exportação de orçamento | Código, Descrição, Un., Qtd., Preço unit. (R$), Total (R$) |

O orçamento tem uma linha por tipo de parede, depois as perdas, o total em R$, o total em EUR (aproximado), a cotação EUR/BRL com a sua data e a base de preço.

## Configuração

Veja a tabela no [README](../../README.pt-BR.md#configuração).

## Idioma da faixa de opções

Cada pasta de botão tem um `bundle.yaml` com um título e uma dica em inglês (`en_us`) e em português do Brasil (`pt_br`). O pyRevit mostra o que corresponde ao idioma do Revit.[^locales] O botão PT / EN altera apenas os rótulos dentro das janelas.

## Módulos

| Módulo | Função |
|---|---|
| `bauser_core.py` | Python puro: conversão de unidades, configuração, preços, numeração, agrupamento, plano de classificação, formatos de número e CSV. Sem importações do Revit |
| `bauser_ids.py` | Python puro: lê um arquivo IDS e verifica os painéis contra ele. Sem importações do Revit |
| `bauser_revit.py` | Adaptador do Revit: monta os painéis a partir das paredes e grava marcas e códigos de classificação |
| `bauser_ui.py` | Janela de resultados em WPF, com a janela de saída do pyRevit como alternativa se o WPF falhar |
| `bauser_text.py` | Textos em português e em inglês e a configuração de idioma |
| `results.xaml` | Layout da janela de resultados |

Principais funções de `bauser_core.py`:

| Função | Retorna |
|---|---|
| `summarize_by_type(panels, basis)` | `[(tipo, quantidade, area_m2, aberturas)]` |
| `number_plan(panels, prefix)` | `[(painel, marca)]` na ordem de numeração |
| `cost_table(panels, waste, rates, basis)` | linhas por painel e totais |
| `budget_lines(panels, waste, rates, basis)` | uma linha por tipo de parede e totais |
| `rate_info(type_name, rates)` | `(preço, código de referência)` |
| `classification_info(type_name, classes)` | `(sistema, código)` |
| `classification_plan(panels, classes)` | `(plano, faltantes)`: os tipos que recebem um código e os que não têm |
| `load_config(path)`, `apply_config(data)`, `parse_config(data)` | Ler, aplicar e verificar a configuração |
| `IDS_ALIASES` | Os apelidos de propriedades IDS configurados, passados a `bauser_ids.check` |
| `fmt(value, digits, lang)`, `money(...)`, `eur(...)` | Números formatados, `en` ou `pt` |
| `write_csv(path, header, rows, delimiter)` | Grava um CSV em UTF-8 |

Funções de `bauser_ids.py`: `parse_ids(source)`, `check(panels, ids, aliases)` e `summarise(rows)`.

Um painel é um dicionário com as chaves `id, mark, type, level, elev, x, y, length_m, height_m, area_m2, gross_m2, openings` e, quando lido do Revit, `irregular`, `properties`, `classification`, `classification_system`, `element` e `type_element`.

## Termos do Revit em português

Os termos abaixo seguem a ajuda da Autodesk em português do Brasil quando ela traz o termo. A coluna de situação diz de que edição da ajuda o termo vem. Os nomes que não foram encontrados na ajuda em português estão marcados, e devem ser conferidos no Revit em português.

| Termo em inglês | Termo em português | Situação |
|---|---|---|
| Properties palette | Paleta Propriedades | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Type Selector | Seletor de tipo | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Edit Type | Editar tipo | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Instance properties, Type properties | Propriedades de instância, Propriedades de tipo | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Unconnected Height | Altura desconectada | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Top Constraint | Restrição superior | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Ribbon | Faixa de opções | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Project Browser | Navegador de projeto | Confirmado, ajuda do Revit 2026[^ptbhelp] |
| Assembly Code | Código de montagem | Confirmado, ajuda do Revit 2012[^ptb] |
| Assembly Description | Descrição da montagem | Confirmado, ajuda do Revit 2012[^ptb] |
| Type Comments | Comentários do tipo | Confirmado, ajuda do Revit 2012[^ptb] |
| Type Mark | Marcação de tipo | Confirmado, ajuda do Revit 2012[^ptb] |
| Identity Data | Dados da identidade | Confirmado, ajuda do Revit 2012[^ptb] |
| Compound structure | Estrutura composta | Confirmado, ajuda do Revit 2027[^ptb2027] |
| Mark | Marca | Não confirmado na ajuda em português. É o nome usado nas janelas desta extensão |
| Area | Área | Não confirmado na ajuda em português |
| Length | Comprimento | Não confirmado na ajuda em português |
| Level, Base Constraint | Nível, Restrição da base | Não confirmado na ajuda em português |
| Edit Profile | Editar perfil | Não confirmado na ajuda em português |
| Classification Number | Número de classificação | Não confirmado na ajuda em português |

[^area]: TAMMIK, Jeremy. Calculating Gross and Net Wall Areas. The Building Coder. [S. l.], [20--]. Disponível em: https://jeremytammik.github.io/tbc/a/1296_spatial_calculator.htm. Acesso em: 20 out. 2026. Citado porque afirma que o parâmetro de área da parede tem as aberturas hospedadas descontadas, e por isso esse parâmetro é usado como valor líquido.
[^bbox]: AUTODESK. Element.BoundingBox Property. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/def2f9f2-b23a-bcea-43a3-e6de41b014c8.htm. Acesso em: 20 out. 2026. Citado pela definição da caixa delimitadora como uma caixa que circunscreve toda a geometria do elemento, o que explica por que ela superestima a altura de paredes editadas, inclinadas e cônicas.
[^findinserts]: AUTODESK. HostObject.FindInserts Method. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/58990230-38cb-3af7-fd25-96ed3215a43d.htm. Acesso em: 20 out. 2026. Citado pela assinatura e pelo significado dos quatro indicadores.
[^wall]: AUTODESK. Wall Class. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/b5891733-c602-12df-beab-da414b58d608.htm. Acesso em: 20 out. 2026. Citado pela propriedade `SketchId`, que é o identificador de elemento inválido quando a parede não tem perfil editado, e pela propriedade `CrossSection`.
[^classparam]: REVITAPIDOCS.COM. API Changes 2026. [S. l.]: revitapidocs.com, 2026. Disponível em: https://www.revitapidocs.com/2026/news. Acesso em: 20 out. 2026. Citado porque lista a mudança na API do Revit 2026 que renomeou `OMNICLASS_CODE` ("OmniClass Number") para `CLASSIFICATION_CODE` ("Classification Number") e `UNIFORMAT_CODE` para `ASSEMBLY_CODE`. O site é um espelho de terceiros da lista de mudanças da Autodesk, e o mesmo texto está espelhado em https://github.com/adskdimitrii/revit-api-ai-friendly-docs/blob/main/2026/ungrouped/Major-changes-and-renovations-to-the-Revit-API.md. Os nomes antigos constam em https://www.revitapidocs.com/2025/fb011c91-be7e-f737-28c7-3f1e1917a0e0.htm.
[^community]: CLASSIFICATION Number (Omniclass) NOT working Revit 2026. Autodesk Community, 12 maio 2026. Disponível em: https://forums.autodesk.com/t5/revit-architecture-forum/classification-number-omniclass-not-working-revit-2026/td-p/14126346. Acesso em: 20 out. 2026. Citado porque uma resposta no tópico diz que a classificação só pode ser usada no editor de famílias e não existe para famílias de sistema, enquanto as notas-chave e os códigos de montagem podem ser usados nos tipos de famílias carregáveis e de sistema. É a declaração de um usuário, e não a documentação da Autodesk.
[^assembly]: AUTODESK. Uniformat Assembly Codes. In: AUTODESK. Revit help. [S. l.]: Autodesk, 2014. Disponível em: https://help.autodesk.com/cloudhelp/2014/ENU/Revit/files/GUID-5900EA95-9702-4054-A849-C0A70EABB2D1.htm. Acesso em: 20 out. 2026. Citado porque diz que o parâmetro Assembly Code é uma propriedade de tipo escolhida na lista Uniformat, e por isso um código da NBR 15965 nele é uma solução de compromisso e o Classification Number é tentado primeiro.
[^setstring]: AUTODESK. Parameter.Set(String) Method. In: AUTODESK. Revit 2026 API Reference. [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/cloudhelp/2026/ENU/Revit-API-MainReference/files/html/956a1e23-cfe5-a60b-1ff9-0e8e33812774.htm. Acesso em: 20 out. 2026. Citado pela regra de que a chamada lança `InvalidOperationException` quando o parâmetro é somente leitura e retorna um valor lógico de sucesso. A página não diz se um parâmetro específico aceita um texto qualquer.
[^ids]: BUILDINGSMART INTERNATIONAL. What is Information Delivery Specification (IDS). [S. l.]: buildingSMART International, 2023. Disponível em: https://www.buildingsmart.org/what-is-information-delivery-specification-ids. Acesso em: 20 out. 2026. Os nomes de elementos, as facetas e os valores de cardinalidade usados pelo leitor vêm do esquema 1.0, https://raw.githubusercontent.com/buildingSMART/IDS/development/Schema/ids.xsd, e dos seus casos de teste em https://github.com/buildingSMART/IDS. Citado porque o leitor os segue.
[^ptb]: AUTODESK. Propriedades de tipo de paredes. In: AUTODESK. Ajuda do Revit 2012. Português (Brasil). [S. l.]: Autodesk, 2012. Disponível em: https://help.autodesk.com/view/RVT/2012/PTB/caas.html?url=caas%2Fvhelp%2Fhelp-dev-autodesk-com%2Fv%2FRevit%2Fptb%2F2012%2FHelp%2F0000-Guia-do-01%2F0325-Construi325%2F0327-Modelage327%2F0328-Paredes328%2F0332-Modifica332%2F0380-Propried380.html. Acesso em: 20 out. 2026. Citado como a redação da própria Autodesk para os parâmetros de tipo de parede: Código de montagem, Descrição da montagem, Comentários do tipo e Marcação de tipo. A página é de uma edição antiga, e os nomes atuais devem ser conferidos na versão do Revit em uso.
[^ptb2027]: AUTODESK. Parâmetros de projeto. In: AUTODESK. Ajuda do Autodesk Revit 2027. Português (Brasil). [S. l.]: Autodesk, 2027. Disponível em: https://help.autodesk.com/cloudhelp/2027/PTB/Revit-Model/files/GUID-24033B80-62D4-4E04-AC15-FA8A6194A64F.htm. Acesso em: 20 out. 2026. Citado porque o sumário da ajuda traz os títulos Estrutura composta e Adicionar ou alterar um código de montagem.
[^ptbhelp]: AUTODESK. Paleta Propriedades. In: AUTODESK. Ajuda do Revit 2026. Português (Brasil). [S. l.]: Autodesk, 2026. Disponível em: https://help.autodesk.com/view/RVT/2026/PTB/?guid=GUID-A764EA7A-FE26-469B-857C-F3A70812FC34. Acesso em: 20 out. 2026. Citado como a redação da própria Autodesk para a paleta Propriedades, o Seletor de tipo, o botão Editar tipo, as propriedades de instância e de tipo, a Altura desconectada e a Restrição superior. A página sobre as partes da interface, com a faixa de opções e o Navegador de projeto, está em https://help.autodesk.com/view/RVT/2026/PTB/?guid=GUID-7793667D-5657-4382-9BEC-F7CB6AC8F53E.
[^locales]: PYREVIT PROJECT. Arquivos pyrevitlib/pyrevit/coreutils/applocales.py e os arquivos de bundle de extensions/pyRevitTools.extension. [S. l.]: pyRevit Labs, [20--]. Disponível em: https://github.com/pyrevitlabs/pyRevit. Acesso em: 20 out. 2026. Citado porque a tabela de idiomas lista `pt_br` como código do português do Brasil, e as extensões do próprio pyRevit dão títulos e dicas sob as chaves `en_us` e `pt_br` em `bundle.yaml`, que é o formato usado aqui.
