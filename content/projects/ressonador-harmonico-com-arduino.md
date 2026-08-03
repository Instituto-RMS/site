+++
title = "Ressonador Harmônico com Arduino"
description = "Demonstração prática de ressonância harmônica: Arduino gera tons de 440Hz e 392Hz que fazem um diapasão vibrar por simpatia."
weight = 10
draft = false

[extra]
status = "Concluído"
tags = [
    "eletrônica",
    "sensoriamento",
    "Física / Som",
]
partners = ""
highlight = false
external_link = ""
start_date = ""
+++


Este projeto pretende demonstrar uma propriedade conhecida no mundo da física como **Ressonância Harmônica**, usando o Arduino Uno como gerador de tons sonoros que nos permite demonstrar o efeito na prática.
Usamos os pinos 8 e 9 do Arduino, sendo o pino 8 configurado como saída digital e o pino 9 como entrada digital. Uma chave seletora conectada ao pino 9 determina a frequência de trabalho: na posição GND o Arduino gera um tom de **440 Hz** (Nota Lá), e em +5V gera **392 Hz**. O sinal passa então por um circuito integrador e um amplificador antes de chegar ao alto-falante.
Usamos um diapasão na frequência de 440 Hz (Nota Lá) que entrará em ressonância — vibrará — à medida que o circuito gere o sinal de frequência correto.
