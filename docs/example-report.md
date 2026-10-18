> **Example report — fictional data.** This is the Markdown the agent writes and the
> person reviews, in the owner's language (Portuguese, in this example). The therapist
> receives it as [`example-report.pdf`](example-report.pdf), rendered by
> `scripts/report_pdf.py` with the numbers, the sentiment chart and the day-by-day grid
> computed from the check-ins. Source ledger: `scripts/fixtures/demo-ledger/`
> (rebuild with `make example-pdf`). Structure and reasons: `skills/sintr/references/report-framework.md`.

---
week: 2026-W42
range: 2026-10-12 → 2026-10-18
status: reviewed
generated_at: 2026-10-18T22:40:00Z
sent_to:
sent_at:
---

# Relatório semanal — Demo Person — 2026-W42

## Como foi a semana <!-- week -->

Foi uma semana puxada no trabalho. Os dois momentos mais difíceis vieram cedo: o planejamento de terça, quando chegaram três demandas de uma vez, e a conversa de feedback de quinta. As duas noites mais curtas da semana vieram antes desses dias. Na sexta veio o melhor momento: uma caminhada sem celular no almoço, a primeira em semanas, e à noite um jantar em família. O domingo à tarde voltou a pesar, como no domingo anterior.

## Para conversar na sessão <!-- session -->

- O feedback do gestor.
- A ansiedade de domingo à tarde, que voltou pelo segundo domingo seguido.
- A pausa no meio do dia, tarefa da última sessão: aconteceu na sexta. Como mantê-la nas semanas de pressão? (sugestão do sintr)
- O que passou pela cabeça antes de aceitar as demandas na terça: "se eu disser que não, vão achar que eu não me esforço". (sugestão do sintr)

## Humor, energia e sono <!-- mood -->

O humor ficou em 2 nos dias do planejamento e do feedback (terça e quinta) e subiu para 4 na sexta e no sábado; a ansiedade fez o caminho inverso, de 4 para 2 e 1. As noites mais curtas foram as que antecederam terça (6h) e quinta (5h30). Não houve check-in na quarta.

- seg 12/10 — "já acordei pensando na sprint"
- ter 13/10 — "acordei cansado"
- qui 15/10 — "fui dormir 1h terminando a entrega"
- sáb 17/10 — "dormi sem despertador"
- dom 18/10 — "domingo à tarde bateu aquela ansiedade de segunda"

## Momentos que marcaram <!-- moments -->

Quatro dos cinco momentos registrados: os dois mais intensos, o melhor da semana e o domingo à tarde, que se repetiu.

### Planejamento com três demandas na mesma sprint <!-- entry-2026-10-13-001 -->
- when: terça, 13 de outubro, à tarde
- tags: trabalho
- happened: Na reunião de planejamento chegaram três demandas novas para a mesma sprint, com o cliente pressionando pelo prazo.
- context: Tinha dormido 6h; a segunda já tinha sido corrida.
- thoughts: "eu não vou dar conta disso" ; "se eu disser que não, vão achar que eu não me esforço"
- felt: ansiedade 85 ; frustração 60
- body: aperto no peito, mandíbula travada
- did: Aceitou as três na hora e trabalhou até as 23h.

### Feedback sobre o ritmo de entrega <!-- entry-2026-10-15-001 -->
- when: quinta, 15 de outubro, à tarde
- tags: trabalho
- happened: Conversa individual com o gestor sobre o ritmo das entregas do mês.
- context: Tinha ido dormir à 1h terminando a entrega (5h30 de sono).
- thoughts: "ele acha que eu sou lento" ; "eu sempre decepciono"
- felt: ansiedade 70 ; vergonha 55
- body: rosto quente, estômago embrulhado
- did: Pediu desculpas várias vezes durante a conversa e ficou calado o resto da tarde.
- evidence_for: Atrasou a entrega de setembro.
- evidence_against: O gestor disse que a qualidade está boa e pediu só mais previsibilidade.
- alternative: "ele pediu previsibilidade, não disse que eu decepciono" (believability: 55)
- felt_after: ansiedade 45 ; vergonha 30

### Caminhada sem celular no almoço <!-- entry-2026-10-16-001 -->
- when: sexta, 16 de outubro, meio-dia
- tags: saúde, trabalho
- happened: Saiu para caminhar vinte minutos no almoço, sem celular, pela primeira vez em semanas.
- thoughts: "devia estar trabalhando" ; "primeira vez em semanas que parei no meio do dia"
- felt: culpa 40 ; alívio 60
- body: respiração mais solta
- did: Voltou e terminou a tarde sem levar trabalho para a noite.

### De novo o domingo à tarde <!-- entry-2026-10-18-001 -->
- when: domingo, 18 de outubro, fim da tarde
- tags: trabalho, eu
- happened: Arrumando as coisas para a semana, no fim da tarde de domingo.
- thoughts: "amanhã começa tudo de novo" ; "não vou dar conta da sprint"
- felt: ansiedade 50 ; tristeza 30
- body: peso no peito
- did: Arrumou a mochila e viu um filme para desligar.

## O que se repetiu <!-- patterns -->

- 11 e 18/10 — No fim da tarde de domingo, ansiedade e o mesmo pensamento: "amanhã começa tudo de novo".
- 13 e 18/10 — "não vou dar conta" apareceu duas vezes, as duas sobre o trabalho.
- 13 e 15/10 — Nos dois momentos mais difíceis, a resposta na hora foi aceitar tudo (13/10) e pedir desculpas várias vezes (15/10).

## O que ajudou <!-- helped -->

- A caminhada sem celular no almoço de sexta (16/10): alívio 60 e "respiração mais solta". Era a tarefa combinada na última sessão.
- O jantar em família na sexta à noite: "fazia tempo que eu não ria assim" (contentamento 60).
- Olhar as evidências depois do feedback de quinta: a ansiedade foi de 70 para 45 e a vergonha de 55 para 30.

---
*Preparado a partir de autorregistros (check-ins e registros estruturados) com a ajuda de um assistente pessoal. Não é avaliação clínica.*
