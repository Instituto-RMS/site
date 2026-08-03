+++
title = "Arco Cantante"
description = "Arco voltaico musical: Arduino + Flyback geram arcos de até 30.000V modulados por áudio via oscilador Hartley."
weight = 10
draft = false

[extra]
status = "Concluído"
tags = [
    "eletrônica",
    "Alta Tensão",
]
partners = ""
highlight = false
external_link = ""
start_date = ""
+++


## Descrição do Circuito
O circuito é composto por uma fonte de alimentação que fornece 5 e 12 Volts com uma corrente entre 3 a 5 Amperes, em nosso caso usamos uma fonte de PC.
A placa de Arduino opera com 5 Vdc e consome no máximo alguns miliamperes, já o oscilador Hartley que funciona sobre um Flyback reaproveitado de uma TV ou monitor de computador, necessita de 12 Vdc e consome entre 3 a 4 Amperes.
A placa de Arduino foi programada com uma sequência de trechos musicais, usando uma biblioteca criada para o Arduino conhecida como **tone**, já o oscilador Hartley funciona com um sistema de bobinas sobre o ferrite do Flyback de forma a criar uma oscilação na faixa de 25 a 50 KHz que gera uma tensão entre 20.000 a 30.000 V, pela bobina de alta tensão do Flyback, o que gera o **Arco Voltaico**. O sinal de áudio gerado pelo Arduino atua na amplitude do sinal do oscilador Hartley de forma que as variações de tensão no Arco Voltaico geram vibrações audíveis.
## Detalhamento Técnico (Esquemático do Circuito)
O coração do projeto é o circuito oscilador Hartley modulado, operando na faixa de frequência de **25 a 50 kHz**.
**Lista de Componentes:**
- Transformador Flyback (TV ou monitor CRT)
- TIP35C
- BC548
- 1N4007
- Resistor 220 Ohms (3W)
- Resistor 22 Ohms (2W)
- Arduino UNO (pino D9)
<img src="/notion/images/projects/arco-cantante/image_a1a53538.png" alt="">
<img src="/notion/images/projects/arco-cantante/0643c5e7-ef95-480b-871b-8e3dab3c4700_5cf69968.png" alt="">
