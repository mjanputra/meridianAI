# Logistics and supply chain forecasting using AI

## 1. Build Focused data pipeline and forecasting model for 1 lane: Shanghai(CNHSA) -> Los Angeles (USLAX)
### Data sources
- SCFI (Shanghai Containerized Freight Index): https://en.sse.net.cn/indices/scfinew.jsp
    - published every Saturday by Shanghai Shipping Exchange, tracks weekly spot rates
- Drewry World Container Index (WCI): https://www.drewry.co.uk/trackers-and-indices/latest-trackers-and-indices
    - Tracks freight rates for 40-foot containers specifically on Shanghai to Los Angeles every Monday
- Bureau of Transportation Statistics (BTS): https://www.bts.gov/freight-indicators
    - publishes freight rate per 40ft container from Shanghai to Los Angeles alongside port-level data including loaded import containers, containership capacity at US ports