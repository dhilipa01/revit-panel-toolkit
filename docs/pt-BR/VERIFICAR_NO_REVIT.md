# Verificar no Revit

[English](../VERIFY_IN_REVIT.md) | [README](../../README.pt-BR.md)

A lógica é testada fora do Revit. Estes passos cobrem o que só uma sessão real do Revit pode mostrar. Use um modelo pequeno, com dois níveis, cerca de oito paredes e dois tipos de parede, desenhadas da esquerda para a direita.

## Botões

1. Clique em Contar painéis. A janela abre e as contagens correspondem ao modelo. Se uma janela de saída simples do pyRevit abrir no lugar, a janela WPF falhou e o rastreamento do erro aparece ali.
2. Teste Numerar painéis primeiro em uma seleção de duas paredes. Ctrl+Z desfaz.
3. Execute Custo dos painéis. Os dois botões de CSV gravam um arquivo que o Excel abre com os acentos intactos.
4. Clique em PT / EN. Os rótulos mudam no clique seguinte.

## Classificação

1. Abra as propriedades de tipo de um tipo de parede e veja se um parâmetro Classification Number (OmniClass Number antes do Revit 2026) aparece na lista. Uma resposta na Comunidade Autodesk diz que ele não aparece para famílias de sistema, como as paredes.
2. Defina um código de classificação para esse tipo de parede em `bauser_config.json` e recarregue o pyRevit.
3. Clique em Classificar painéis. A linha de resultado indica o parâmetro gravado, Classification Number ou Código de montagem, e diz Gravado.
4. Abra de novo as propriedades de tipo e leia esse parâmetro. Ele deve conter o código.
5. Se a linha disser Somente leitura ou Sem parâmetro, anote a versão do Revit e os nomes de parâmetros que aparecem na lista. Ainda não foi confirmado se algum dos dois parâmetros aceita um código que não esteja no arquivo de classificação do próprio Revit.
6. Ctrl+Z desfaz a alteração para todas as paredes desse tipo.

## Verificação IDS

1. Clique em Verificar IDS e escolha `examples/panel_requirements.ids`.
2. Uma parede sem Marca, sem código de classificação ou sem o parâmetro de resistência ao fogo mostra Não atende nesse requisito.
3. Dê a um tipo de parede um valor de resistência ao fogo e um código de classificação, numere os painéis e clique de novo. Esse painel deve atender aos três requisitos.
4. Veja um nome de propriedade que difere do nome do Revit só no espaçamento, como `FireRating` e Fire Rating. Ele deve corresponder.
5. Em um Revit com a interface traduzida, como o português, veja o nome de parâmetro que o Revit mostra para a resistência ao fogo, acrescente-o a `ids_aliases` em `bauser_config.json`, recarregue o pyRevit e clique em Verificar IDS de novo. O requisito deve passar a ser atendido.
6. A janela diz que a verificação foi feita nos parâmetros do Revit, e não em um arquivo IFC. Um modelo exportado para IFC também deve ser verificado com uma ferramenta de IFC.

## Área líquida e tamanho total do painel

1. Tome uma parede simples, com extremidades livres e sem aberturas. O seu parâmetro Área deve ser igual ao seu Comprimento vezes a altura. Se não for, a Área do Revit e o comprimento vezes altura desta extensão medem coisas diferentes.
2. Adicione uma porta. A área líquida cai pelo recorte da porta, o tamanho total do painel não muda e Aberturas mostra 1.
3. Una duas paredes em um canto e compare os dois valores. Uma pequena diferença indicaria que a Área do Revit usa faces aparadas, enquanto esta extensão usa o comprimento da linha de localização. As fontes divergem e a Autodesk não diz.
4. Edite o perfil de uma parede, por exemplo recortando um canto. O aviso da base de tamanho total do painel deve aparecer.
5. Anexe o topo de uma parede a uma cobertura inclinada. Nenhum aviso aparece, o que é uma lacuna conhecida, e o tamanho total do painel fica alto demais.

## Outros pontos

- Paredes que já compartilham um valor de Marca em outra parte do modelo podem acionar o aviso de Marca duplicada do Revit. Use um modelo limpo para a verificação.
- O Revit 2024 e os posteriores leem os valores de ElementId por uma propriedade diferente da das versões anteriores. O código trata as duas, e nenhuma foi executada em uma instalação real.
- A Autodesk renomeou os parâmetros OmniClass e Uniformat na API do Revit 2026.[^rename] O código tenta os dois nomes. Anote qual deles a sua versão do Revit tem.
- Com a interface do Revit em português do Brasil, a faixa de opções mostra os títulos dos botões em português. Confira se os seis títulos e dicas aparecem e se nenhum está cortado.

[^rename]: REVITAPIDOCS.COM. API Changes 2026. [S. l.]: revitapidocs.com, 2026. Disponível em: https://www.revitapidocs.com/2026/news. Acesso em: 20 out. 2026. Citado pela mudança na API do Revit 2026 que renomeou `OMNICLASS_CODE` para `CLASSIFICATION_CODE` e `UNIFORMAT_CODE` para `ASSEMBLY_CODE`. O site é um espelho de terceiros da lista de mudanças da Autodesk.
