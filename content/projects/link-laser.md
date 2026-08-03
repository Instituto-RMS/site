+++
title = "Link LASER"
description = "Transmissão de áudio por feixe LASER: Arduino modula música via luz, captada por transistor 2N3055 adaptado como fotoreceptor fotovoltaico."
weight = 10
draft = false

[extra]
status = "Concluído"
tags = [
    "eletrônica",
    "sensoriamento",
    "telemetria",
]
partners = ""
highlight = false
external_link = ""
start_date = ""
+++


O circuito é composto por uma fonte de alimentação que fornece 5 Volts com uma corrente de 1 Ampere — no nosso caso, baterias. A placa Arduino gera uma sequência de trechos musicais usando a biblioteca **pitch** e envia o sinal pelo pino digital D9 para um circuito acoplador/drive, que por sua vez alimenta um diodo LASER de 1 mW com o sinal modulado em amplitude. O resultado é um feixe LASER cujo brilho varia no ritmo da música.
O truque mais interessante está na recepção: abrimos o encapsulamento de um transistor 2N3055 para expor o cristal de silício, transformando-o num fotorreceptor fotovoltaico — ele gera seu próprio sinal elétrico ao ser atingido pelo LASER, sem precisar de nenhuma fonte externa. Esse sinal, que varia conforme a modulação do brilho, é então encaminhado direto para uma caixa amplificadora de áudio, e pronto: a música atravessa o ar num feixe de luz.
Além do Arduino e do diodo LASER, a montagem leva um transistor BC548, um potenciômetro de 10 kΩ, um capacitor eletrolítico de 15 µF, dois capacitores cerâmicos e alguns resistores — tudo coisa simples, mas que junta óptica, eletrônica e uma gambiarra de respeito com o 2N3055.
<img src="/notion/images/projects/link-laser/image_5023b5bb.png" alt="">
