### Notizen

- Ein Agent kann viele Tools verwenden
- Keine Teams? Keine Interaktion zwischen Agenten? --> Gibt zumindest keine klassischen Team (vgl. AutoGen)
    -> Großer Anwendungseinsatz schwierig?
        -> Durch Tools wie Mem0 oder sonstiges ausgleichbar?
    -> Einsatz für kleine, smarte Anwendungsfälle
- Umgang mit lokalen Pfaden; durchsucher aller Dateien --> Nutzung von lokalem llama nicht möglich
- Schweres Tracking wenn Agenten als Tool auftreten
- Daten an andere Agenten weitergeben durch Tool schwierig
- Was geht in die AgentAsTools rein?
- Tool-Call AUfschlüsselung -> Name der aufgerufenen Tools nicht zugreifbar, warum!? -> Logging in genutzten Tools, wenn nur von einem Agent genutzt
- WUnsch, dass Logging wäre "Agent X ruft Tool Y mit Eingaben Z auf ... Agent X erhält von Tool Y Ausgabe Z'"
- Nicht deterministisch (offenkundig), falsche File-Referenz
- Kontext als Problem, wenn File nicht gefunden wird -> Sonst: Lesen aller Files als Approach
- Schwierigkeiten einen funktionierenden "Workflow" zu finden; Musst mehr oder weniger je Framework angepasst werden
- Kein nativer lokaler Ollama Support; viele Errors

- AutoGen: Nennung eines Wortes als Endbedninung seltsam


---

- Let the planner identify the issue, or, the coder and invent a new agent "implementator"
- Only work on one file at a time?