
## 4. Servicekonzept

### Servicebeschreibung

- **Name:** CurrencyConversionService  
- **Funktion:** Umrechnung von Beträgen zwischen Währungen  
- **Schnittstelle:** REST API, z.B.:  
  `GET /convert?from=EUR&to=USD&amount=100`  
- **Antwort:** JSON mit dem umgerechneten Betrag

### Service-Level-Agreements (SLAs)

- Verfügbarkeit: 99,9%  
- Antwortzeit: < 500 ms  
- Genauigkeit: Tägliche Aktualisierung der Wechselkurse  
- Wartung: Täglich 02:00-02:30 Uhr

### Rollen und Verantwortlichkeiten

| Rolle          | Verantwortlichkeit                       |
|----------------|----------------------------------------|
| IT-Team        | Betrieb und Wartung                     |
| Fremdsysteme   | Nutzung und Fehlerreporting             |
| Support-Team   | Support und Störungsbehebung           |
| Business Owner | Anforderungen und geschäftliche Verantwortung |

### Key Performance Indicators (KPIs)

- Anzahl erfolgreicher Umrechnungen  
- Durchschnittliche Antwortzeit  
- Verfügbarkeit des Services  
- Anzahl Fehlerberichte  
- Aktualität der Wechselkurse

## 5. Integration in den übergeordneten Prozess

Der Service wird von Fremdsystemen genutzt, um Beträge automatisiert und präzise umzuwandeln. Dies optimiert Finanzprozesse, erhöht die Effizienz und reduziert Fehler.

---
