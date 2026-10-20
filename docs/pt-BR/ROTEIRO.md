# Roteiro

[English](../ROADMAP.md) | [README](../../README.pt-BR.md)

Trabalho em aberto, na ordem em que provavelmente será feito. Os itens concluídos continuam na lista para que a direção fique visível.

## Concluído

- [x] Contar, numerar e calcular o preço de painéis de parede pela faixa de opções
- [x] Preço pela área líquida e pelo tamanho total do painel
- [x] Aberturas por painel com `FindInserts`
- [x] Aviso para paredes com perfil editado ou com seção inclinada ou cônica
- [x] Rótulos em português e em inglês
- [x] Valor em reais com um valor aproximado em euros
- [x] CSV por painel e CSV de orçamento
- [x] Configuração em um arquivo JSON
- [x] Código de classificação por tipo de parede
- [x] Verificação IDS contra os parâmetros do Revit
- [x] Alternativa do Código de montagem para o código de classificação e apelidos IDS para nomes de parâmetros traduzidos
- [x] Documentação em português do Brasil e títulos e dicas da faixa de opções em português
- [x] Testes que rodam fora do Revit, verificação de estilo e CI
- [x] Fluxo de publicação e metadados da extensão

## Próximos

- [ ] Rodar a extensão em uma sessão real do Revit e registrar os resultados ([lista de verificação](VERIFICAR_NO_REVIT.md))
- [ ] Adicionar capturas de tela com um único estilo de moldura: mesma proporção, margem, raio de borda e moldura de janela
- [ ] Confirmar no Revit se o Classification Number existe nos tipos de parede, se algum dos parâmetros aceita o código e em quais versões do Revit
- [ ] Preencher a tabela de apelidos IDS com os nomes de parâmetros que um Revit em português mostra
- [ ] Detectar paredes com topo ou base anexados
- [ ] Verificar um arquivo IFC exportado contra um arquivo IDS, e não só os parâmetros do Revit
- [ ] Uma revisão da documentação em português por um falante nativo que trabalhe com o Revit

## Depois

- [ ] Dividir uma parede em painéis
- [ ] Detalhamento automático de painéis para produção em fábrica
- [ ] Criar uma montagem de painel com as suas vistas e a sua folha, para desenhos de fabricação
- [ ] Exportar uma lista de corte para a produção em fábrica
- [ ] Etiquetas de painel com código QR ou de barras e um status para cada painel, que os produtos de enquadramento existentes oferecem[^onyx]
- [ ] Arquivos para perfiladoras e máquinas de painéis, quando a máquina de destino e o seu formato forem conhecidos
- [ ] Verificação de interfaces para os temas da NBR 16970-3: parede e laje, parede e abertura, sistemas mistos
- [ ] Uma versão assinada e um instalador, que as diretrizes de publicação da Autodesk pedem[^publisher]
- [ ] Cotação ao vivo com data e moedas que o PTAX não cobre (ARS, UYU, PYG)

Ideias e erros vão em [Issues](https://github.com/dhilipa01/revit-panel-toolkit/issues).

[^onyx]: GRAITEC STRUCSOFT. Production management software. [S. l.]: Graitec, [20--]. Disponível em: https://strucsoftsolutions.com/solutions/production-management-software. Acesso em: 20 out. 2026. Citado porque mostra o rastreamento de cada painel com códigos QR e de barras na fabricação, no empilhamento e na expedição em um produto existente, que é o modelo para o item das etiquetas. É a descrição do próprio fornecedor.
[^publisher]: AUTODESK PLATFORM SERVICES. Revit publisher guidelines. [S. l.]: Autodesk, 2023. Disponível em: https://aps.autodesk.com/marketplace/publisher-center/revit-publisher-guidelines. Acesso em: 20 out. 2026. Citado pelos requisitos da loja sobre um botão na faixa de opções, um manifesto de complemento e um instalador sem etapas manuais. O Revit também avisa sobre complementos sem assinatura confiável: https://help.autodesk.com/cloudhelp/2022/ENU/Revit-Troubleshooting/files/GUID-36D29367-A540-4CFD-9773-4995BF1DF08A.htm.
