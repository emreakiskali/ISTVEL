import streamlit as st
import requests
import pandas as pd
import folium
try:
    import plotly.graph_objects as go
    PLOTLY_OK = True
except ImportError:
    PLOTLY_OK = False
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import numpy as np
import os
import subprocess
import zipfile
import io
import time
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
import tempfile

# ── osmnx import (opsiyonel — kurulu değilse SUMO export devre dışı) ─────────
try:
    import osmnx as ox
    OSMNX_OK = True
except ImportError:
    OSMNX_OK = False

# ══════════════════════════════════════════════════════════════════════════════
#  DİL / LANGUAGE STRINGS
# ══════════════════════════════════════════════════════════════════════════════
LANG = {
    "TR": {
        "page_title":        "ISTVEL — İstanbul EV Simülasyonu",
        "app_title":         "⚡ ISTVEL — Istanbul Simulation Tool for Vehicle Electrification",
        "app_caption":       "İBB Açık Veri Portalı — Saatlik Trafik Analizi → SUMO Simülasyonu",
        "filters":           "⚙️ Filtreler",
        "month":             "📅 Ay seçin",
        "all_hours":         "Tüm saatler",
        "hour":              "🕐 Saat",
        "all_days":          "Tüm günler",
        "day":               "📆 Ayın günü",
        "viz_mode":          "🗺️ Görselleştirme modu",
        "viz_heat":          "🔥 Isı Haritası",
        "viz_circle":        "🔵 Daire (Araç Sayısı)",
        "viz_cluster":       "📍 Küme (Cluster)",
        "popup_datetime":    "Tarih/Saat",
        "popup_vehicles":    "Araç",
        "popup_avg_speed":   "Ort. Hız",
        "popup_minmax":      "Min/Maks",
        "record_limit":      "📊 Kayıt limiti",
        "load_btn":          "🔄 Veriyi Yükle",
        "ev_settings":       "⚡ EV & Şarj Ayarları",
        "cs_interval":       "📍 Şarj İstasyonu Aralığı (km)",
        "cs_power":          "⚡ Şarj Gücü (kW)",
        "cs_efficiency":     "🔋 Şarj Verimliliği",
        "cs_transit":        "🚗 Hareket halinde şarj (chargeInTransit)",
        "cs_length":         "📏 İstasyon Boyu (m)",
        "cs_delay":          "⏱️ Şarj Gecikmesi (s)",
        "lang_label":        "🌐 Dil / Language",
        "cells":             "📍 Hücre",
        "total_veh":         "🚗 Toplam Araç",
        "avg_speed":         "⚡ Ort. Hız",
        "max_veh":           "📈 Maks Araç",
        "hour_day":          "🕐 Saat / Gün",
        "map_title":         "🗺️",
        "speed_dist":        "#### 📊 Hız Dağılımı",
        "fast":              "Hızlı",
        "medium":            "Orta",
        "slow":              "Yavaş",
        "hourly":            "#### ⏰ Saatlik",
        "raw_data":          "📋 Ham Veri",
        "csv_dl":            "⬇️ CSV İndir",
        "sumo_title":        "## 🚗 SUMO'ya Aktar",
        "osmnx_warn":        "**osmnx kurulu değil.**",
        "export_settings":   "#### ⚙️ Export Ayarları",
        "region_select":     "🏙️ Bölge seçin",
        "region_help":       "Seçili bölgenin yol ağı OSM'den çekilir ve IBB verisi bu bölgeye filtrelenir.",
        "manual_select":     "✏️ Haritadan Elle Seç",
        "manual_hint":       "Haritaya tıklayarak 3-8 nokta seçin. Seçilen noktaların etrafında bir alan oluşturulacak.",
        "manual_clear":      "🗑️ Noktaları Temizle",
        "manual_points":     "seçili nokta",
        "manual_need_more":  "⚠️ En az 3 nokta seçin.",
        "manual_bbox_ready": "✅ Özel alan hazır",
        "manual_map_click":  "🖱️ Haritaya tıklayarak nokta ekleyin:",
        "manual_padding":    "🔲 Alan genişletme (derece)",
        "points_found":      "İBB noktası bulundu.",
        "netconvert_chk":    "🔧 netconvert ile .net.xml üret",
        "netconvert_help":   "SUMO kurulu ise net.xml otomatik oluşturulur.",
        "output_files":      "#### 📦 Çıktı Dosyaları",
        "no_data_warn":      "⚠️ Seçili bölgede veri yok. Farklı bölge veya ay seçin.",
        "fleet_mode":        "🚘 Filo Modu",
        "fleet_ev":          "⚡ EV",
        "fleet_fuel":        "⛽ FUEL",
        "fleet_hybrid":      "🔀 HYBRID",
        "hybrid_ev_ratio":   "🔋 EV oranı (%)",
        "export_btn":        "🚀 SUMO Paketi Oluştur",
        "fetching_osm":      "🗺️ OSM yol ağı çekiliyor…",
        "snapping":          "📍 İBB noktaları yol kenarlarına eşleştiriliyor…",
        "generating":        "📄 SUMO dosyaları üretiliyor…",
        "generating_cs":     "⚡ Generating charging stations…",
        "zip_ready":         "🎉 SUMO paketi hazır!",
        "zip_dl":            "⬇️ SUMO Paketini İndir (.zip)",
        "validation_map":    "🗺️ Eşleştirme Doğrulama Haritası — Mavi=IBB noktası, Renkli çizgi=Edge (kırmızı=yoğun)",
        "start_hint":        "Başlamak için sol paneli kullanın",
        "start_hint2":       'Ay ve saat seçin, ardından <b>"Veriyi Yükle"</b> butonuna tıklayın.',
        "analysis_title":    "## 📊 Simülasyon Analizi",
        "analysis_desc":     "SUMO simülasyonunu çalıştırdıktan sonra oluşan `output/tripinfo.xml` ve `output/emission.xml` dosyalarını yükleyin.",
        "color_legend":      "**Renk:** 🟢 Hızlı ≥60 km/h  🟠 Orta 30-60  🔴 Yavaş <30",
        # Dosya yükleme
        "upload_trip":       "📂 tripinfo.xml yükle",
        "upload_emis":       "📂 emission.xml yükle",
        "upload_batt":       "📂 battery.xml yükle (EV)",
        # Özet kartlar
        "sim_summary":       "### 🏁 Simülasyon Özeti",
        "met_total_veh":     "🚗 Toplam Araç",
        "met_arrived":       "✅ Varışa Ulaşan",
        "met_avg_route":     "📏 Ort. Rota",
        "met_avg_dur":       "⏱️ Ort. Süre",
        "met_avg_spd":       "⚡ Ort. Hız",
        "met_avg_wait":      "⏳ Ort. Bekleme",
        # Yakıt & emisyon
        "fuel_emis_summary": "### ⛽ Yakıt & Emisyon Özeti",
        "met_total_fuel_l":  "⛽ Toplam Yakıt",
        "met_total_fuel_g":  "⛽ Yakıt (g)",
        "met_total_co2":     "💨 Toplam CO₂",
        "met_total_nox":     "🔬 Toplam NOx",
        "met_total_pm":      "🏭 Toplam PM",
        "met_avg_noise":     "🔊 Ort. Gürültü",
        "per_veh_avgs":      "**Araç Başına Ortalamalar:**",
        "met_perveh_fuel":   "⛽ Araç Başı Yakıt",
        "met_perveh_co2":    "💨 Araç Başı CO₂",
        "met_perveh_nox":    "🔬 Araç Başı NOx",
        "met_perveh_pm":     "🏭 Araç Başı PM",
        "met_avg_fuelkm":    "⛽ Ort. Yakıt/km",
        "met_min_fuelkm":    "⛽ Min Yakıt/km",
        "met_max_fuelkm":    "⛽ Maks Yakıt/km",
        "met_avg_co2km":     "💨 Ort. CO₂/km",
        # Grafikler
        "dist_charts":       "### 📈 Dağılım Grafikleri",
        "chart_route":       "**🗺️ Rota Uzunluğu Dağılımı (km)**",
        "chart_speed":       "**⚡ Ortalama Hız Dağılımı (km/h)**",
        "chart_fuel":        "**⛽ Yakıt Tüketimi Dağılımı (g)**",
        "chart_co2":         "**💨 CO₂ Emisyonu Dağılımı (g)**",
        "chart_nox":         "**🔬 NOx Dağılımı (mg)**",
        "chart_noise":       "**🔊 Gürültü Dağılımı (dB)**",
        "col_route":         "Rota (km)",
        "col_speed":         "Hız (km/h)",
        "col_fuel_g":        "Yakıt (g)",
        "col_co2_g":         "CO₂ (g)",
        "col_nox":           "NOx (mg)",
        "col_noise":         "Gürültü (dB)",
        "col_vehicles":      "Araç Sayısı",
        "col_veh":           "Araç",
        # Araç bazlı tablo
        "veh_detail":        "### 🔍 Araç Bazlı Detay",
        "col_vid":           "Araç ID",
        "col_dur":           "Süre (s)",
        "col_avgspd":        "Ort. Hız (km/h)",
        "col_wait":          "Bekleme (s)",
        "col_fuel_l":        "Yakıt (L)",
        "col_nox_mg":        "NOx (mg)",
        "col_pm_mg":         "PM (mg)",
        "col_noise_db":      "Gürültü (dB)",
        "col_elec_kwh":      "Elektrik (kWh)",
        "col_net_kwh":       "Net kWh",
        "col_kwh_km":        "kWh/km",
        "col_soc":           "SoC %",
        "col_charge_ev":     "Şarj Olayı",
        "col_co2_km":        "CO₂/km (g)",
        "btn_veh_csv":       "⬇️ Araç Raporu CSV",
        # EV batarya
        "ev_battery":        "### ⚡ EV Batarya & Elektrik Tüketimi",
        "met_total_cons":    "⚡ Toplam Tüketim",
        "met_net_cons":      "🔋 Net Tüketim",
        "met_total_charge":  "🔌 Toplam Şarj",
        "met_avg_soc":       "🔋 Ort. Bitiş SoC",
        "met_perveh_kwh":    "⚡ Araç Başı",
        "met_avg_kwhkm":     "⚡ Ort. kWh/km",
        "met_min_kwhkm":     "⚡ Min kWh/km",
        "met_max_kwhkm":     "⚡ Maks kWh/km",
        "chart_soc":         "**🔋 Bitiş SoC Dağılımı (%)**",
        "chart_ec":          "**⚡ Tüketim Dağılımı (kWh)**",
        # Yakıt vs Elektrik
        "fuel_vs_ev":        "### 🔄 Yakıt vs Elektrik Karşılaştırması",
        "met_total_fuel":    "⛽ Toplam Yakıt",
        "met_ev_net":        "⚡ EV Net Tüketim",
        "met_energy_save":   "🌱 Enerji Tasarrufu",
        "met_co2_compare":   "💨 CO₂: Yakıt → EV",
        "met_less":          "az",
        "methodology":       (
            "**Metodoloji:**  "
            "Yakıt yoğunluğu **820 g/L** (820 000 mg/L, motorin EN 590).  "
            "SUMO `--emission-output.step-scaled` aktif → her timestep değeri zaten toplam mg (mg/s × step_s).  "
            "Toplam yakıt = {fuel_mg:,.0f} mg → {fuel_g:,.3f} g → **{fuel_l:,.4f} L** (÷ 820 000).  "
            "1 L motorin ≈ {kwh_per_l} kWh (alt ısıl değer).  "
            "EV CO₂: {ev_kwh:.1f} kWh × 0.45 kg/kWh (Türkiye şebeke faktörü) = {co2_ev:.1f} kg."
        ),
        "perveh_fuel_ev":    "**Araç bazlı yakıt vs elektrik (ilk 20):**",
        "btn_compare_csv":   "⬇️ Karşılaştırma CSV",
        "col_rota":          "Rota (km)",
        "col_fuel_compare":  "Yakıt (g)",
        "col_fuel_l_cmp":    "Yakıt (L)",
        "col_elec_cmp":      "Elektrik (kWh)",
        # Saatlik profil
        "hourly_profile":    "### ⏰ Saatlik Yakıt & CO₂ Profili",
        "chart_fuel_min":    "**⛽ Dakikalık Toplam Yakıt (g)**",
        "chart_co2_min":     "**💨 Dakikalık Toplam CO₂ (g)**",
        "col_minute":        "Dakika",
        "col_fuel_g2":       "Yakıt_g",
        "col_co2_g2":        "CO2_g",
        "readme_title":      "ISTVEL — İSTANBUL TRAFİK → SUMO PAKETİ",
        "readme_region":     "Bölge",
        "readme_month":      "Ay",
        "readme_hour":       "Saat",
        "readme_all":        "Tümü",
        "readme_fleet":      "Filo Modu",
        # Karşılaştırmalı analiz sekmeleri
        "tab_ev":            "⚡ EV Filosu",
        "tab_fuel":          "⛽ Yakıtlı Filo",
        "tab_hybrid":        "🔄 Hibrit Filo",
        "tab_compare":       "📊 Karşılaştırma",
        "cost_settings":     "💰 Maliyet Parametreleri",
        "fuel_price":        "⛽ Akaryakıt Fiyatı (₺/L)",
        "fuel_price_help":   "Güncel motorin fiyatı için Shell sitesini kontrol edin",
        "elec_price":        "⚡ Elektrik Fiyatı (₺/kWh)",
        "elec_price_help":   "ZES DC tarife (07.01.2026 itibarıyla 16.49 ₺/kWh)",
        "no_files":          "📂 Bu sekme için henüz dosya yüklenmedi.",
        "fleet_summary":     "### 🏁 Filo Özeti",
        "cost_summary":      "### 💰 Maliyet Özeti",
        "met_fuel_cost":     "💸 Yakıt Maliyeti",
        "met_elec_cost":     "💸 Elektrik Maliyeti",
        "met_cost_perveh":   "💸 Araç Başı Maliyet",
        "met_cost_per100km": "💸 100 km Maliyet",
        "compare_title":     "## 🏆 EV / Yakıt / Hibrit Karşılaştırması",
        "compare_desc":      "Üç sekmeye de dosya yüklendiğinde karşılaştırma otomatik görünür.",
        "compare_energy":    "### ⚡ Enerji Tüketimi",
        "compare_emission":  "### 💨 Emisyon",
        "compare_cost":      "### 💰 Toplam Maliyet (₺)",
        "compare_perveh":    "### 🚗 Araç Başına",
        "col_fleet":         "Filo",
        "col_total_cost":    "Toplam Maliyet (₺)",
        "col_cost_perveh":   "Araç Başı (₺)",
        "col_kwh_total":     "Toplam kWh",
        "col_fuel_total_l":  "Toplam Yakıt (L)",
        "col_co2_total":     "Toplam CO₂ (kg)",
        "saving_vs_fuel":    "💚 Yakıt'a göre EV tasarruf",
        "shell_link":        "🔗 Shell akaryakıt fiyatları",
        "zes_link":          "🔗 ZES fiyatlandırma",
        "currency_label":    "💱 Para Birimi",
        "tab_cs":            "🔌 Şarj İstasyonları",
        "cs_upload_trip":    "📂 chargingstations_output.xml yükle",
        "cs_title":          "### 🔌 Şarj İstasyonu Analizi",
        "cs_no_data":        "chargingstations_output.xml yükleyin (SUMO → output/chargingstations_output.xml).",
        "cs_total_charged":  "⚡ Toplam Şarj (kWh)",
        "cs_events":         "🔌 Şarj Olayları",
        "cs_avg_soc_start":  "🔋 Ort. Başlangıç SoC",
        "cs_avg_soc_end":    "🔋 Ort. Bitiş SoC",
        "cs_cost_per_kwh":   "⚡ Şarj Fiyatı (birim/kWh)",
        "cs_total_cost":     "💰 Toplam Şarj Maliyeti",
        "cs_vehicles_charged": "🚗 Şarj Olan Araçlar",
        "cs_avg_charged_veh": "⚡ Araç Başı Şarj (kWh)",
        "cs_compare_label":  "Şarj İstasyonları",
    },
    "EN": {
        "page_title":        "ISTVEL — Istanbul EV Simulation",
        "app_title":         "⚡ ISTVEL — Istanbul Simulation Tool for Vehicle Electrification",
        "app_caption":       "IBB Open Data Portal — Hourly Traffic Analysis → SUMO Simulation",
        "filters":           "⚙️ Filters",
        "month":             "📅 Select month",
        "all_hours":         "All hours",
        "hour":              "🕐 Hour",
        "all_days":          "All days",
        "day":               "📆 Day of month",
        "viz_mode":          "🗺️ Visualisation mode",
        "viz_heat":          "🔥 Heat Map",
        "viz_circle":        "🔵 Circle (Vehicle Count)",
        "viz_cluster":       "📍 Cluster",
        "popup_datetime":    "Date/Time",
        "popup_vehicles":    "Vehicles",
        "popup_avg_speed":   "Avg. Speed",
        "popup_minmax":      "Min/Max",
        "record_limit":      "📊 Record limit",
        "load_btn":          "🔄 Load Data",
        "ev_settings":       "⚡ EV & Charging Settings",
        "cs_interval":       "📍 Charging Station Interval (km)",
        "cs_power":          "⚡ Charging Power (kW)",
        "cs_efficiency":     "🔋 Charging Efficiency",
        "cs_transit":        "🚗 Charge while moving (chargeInTransit)",
        "cs_length":         "📏 Station Length (m)",
        "cs_delay":          "⏱️ Charge Delay (s)",
        "lang_label":        "🌐 Language / Dil",
        "cells":             "📍 Cells",
        "total_veh":         "🚗 Total Vehicles",
        "avg_speed":         "⚡ Avg Speed",
        "max_veh":           "📈 Max Vehicles",
        "hour_day":          "🕐 Hour / Day",
        "map_title":         "🗺️",
        "speed_dist":        "#### 📊 Speed Distribution",
        "fast":              "Fast",
        "medium":            "Medium",
        "slow":              "Slow",
        "hourly":            "#### ⏰ Hourly",
        "raw_data":          "📋 Raw Data",
        "csv_dl":            "⬇️ Download CSV",
        "sumo_title":        "## 🚗 Export to SUMO",
        "osmnx_warn":        "**osmnx not installed.**",
        "export_settings":   "#### ⚙️ Export Settings",
        "region_select":     "🏙️ Select region",
        "region_help":       "The road network for the selected region is fetched from OSM and IBB data is filtered to this area.",
        "manual_select":     "✏️ Draw Selection on Map",
        "manual_hint":       "Click on the map to place 3–8 points. A bounding area will be created around them.",
        "manual_clear":      "🗑️ Clear Points",
        "manual_points":     "points selected",
        "manual_need_more":  "⚠️ Select at least 3 points.",
        "manual_bbox_ready": "✅ Custom area ready",
        "manual_map_click":  "🖱️ Click on the map to add points:",
        "manual_padding":    "🔲 Area padding (degrees)",
        "points_found":      "IBB points found.",
        "netconvert_chk":    "🔧 Generate .net.xml with netconvert",
        "netconvert_help":   "If SUMO is installed, net.xml is generated automatically.",
        "output_files":      "#### 📦 Output Files",
        "no_data_warn":      "⚠️ No data for selected area. Try a different region or month.",
        "fleet_mode":        "🚘 Fleet Mode",
        "fleet_ev":          "⚡ EV",
        "fleet_fuel":        "⛽ FUEL",
        "fleet_hybrid":      "🔀 HYBRID",
        "hybrid_ev_ratio":   "🔋 EV ratio (%)",
        "export_btn":        "🚀 Generate SUMO Package",
        "fetching_osm":      "🗺️ Fetching OSM road network…",
        "snapping":          "📍 Snapping IBB points to road edges…",
        "generating":        "📄 Generating SUMO files…",
        "generating_cs":     "⚡ Generating charging stations…",
        "zip_ready":         "🎉 SUMO package ready!",
        "zip_dl":            "⬇️ Download SUMO Package (.zip)",
        "validation_map":    "🗺️ Snap Validation Map — Blue=IBB point, Coloured line=Edge (red=dense)",
        "start_hint":        "Use the left panel to get started",
        "start_hint2":       'Select month and hour, then click <b>"Load Data"</b>.',
        "analysis_title":    "## 📊 Simulation Analysis",
        "analysis_desc":     "After running the SUMO simulation, upload `output/tripinfo.xml` and `output/emission.xml`.",
        "color_legend":      "**Colour:** 🟢 Fast ≥60 km/h  🟠 Medium 30-60  🔴 Slow <30",
        # File upload
        "upload_trip":       "📂 Upload tripinfo.xml",
        "upload_emis":       "📂 Upload emission.xml",
        "upload_batt":       "📂 Upload battery.xml (EV)",
        # Summary cards
        "sim_summary":       "### 🏁 Simulation Summary",
        "met_total_veh":     "🚗 Total Vehicles",
        "met_arrived":       "✅ Arrived",
        "met_avg_route":     "📏 Avg. Route",
        "met_avg_dur":       "⏱️ Avg. Duration",
        "met_avg_spd":       "⚡ Avg. Speed",
        "met_avg_wait":      "⏳ Avg. Wait",
        # Fuel & emission
        "fuel_emis_summary": "### ⛽ Fuel & Emission Summary",
        "met_total_fuel_l":  "⛽ Total Fuel",
        "met_total_fuel_g":  "⛽ Fuel (g)",
        "met_total_co2":     "💨 Total CO₂",
        "met_total_nox":     "🔬 Total NOx",
        "met_total_pm":      "🏭 Total PM",
        "met_avg_noise":     "🔊 Avg. Noise",
        "per_veh_avgs":      "**Per-Vehicle Averages:**",
        "met_perveh_fuel":   "⛽ Fuel / Vehicle",
        "met_perveh_co2":    "💨 CO₂ / Vehicle",
        "met_perveh_nox":    "🔬 NOx / Vehicle",
        "met_perveh_pm":     "🏭 PM / Vehicle",
        "met_avg_fuelkm":    "⛽ Avg. Fuel/km",
        "met_min_fuelkm":    "⛽ Min Fuel/km",
        "met_max_fuelkm":    "⛽ Max Fuel/km",
        "met_avg_co2km":     "💨 Avg. CO₂/km",
        # Charts
        "dist_charts":       "### 📈 Distribution Charts",
        "chart_route":       "**🗺️ Route Length Distribution (km)**",
        "chart_speed":       "**⚡ Average Speed Distribution (km/h)**",
        "chart_fuel":        "**⛽ Fuel Consumption Distribution (g)**",
        "chart_co2":         "**💨 CO₂ Emission Distribution (g)**",
        "chart_nox":         "**🔬 NOx Distribution (mg)**",
        "chart_noise":       "**🔊 Noise Distribution (dB)**",
        "col_route":         "Route (km)",
        "col_speed":         "Speed (km/h)",
        "col_fuel_g":        "Fuel (g)",
        "col_co2_g":         "CO₂ (g)",
        "col_nox":           "NOx (mg)",
        "col_noise":         "Noise (dB)",
        "col_vehicles":      "Vehicle Count",
        "col_veh":           "Vehicles",
        # Per-vehicle table
        "veh_detail":        "### 🔍 Per-Vehicle Details",
        "col_vid":           "Vehicle ID",
        "col_dur":           "Duration (s)",
        "col_avgspd":        "Avg. Speed (km/h)",
        "col_wait":          "Wait (s)",
        "col_fuel_l":        "Fuel (L)",
        "col_nox_mg":        "NOx (mg)",
        "col_pm_mg":         "PM (mg)",
        "col_noise_db":      "Noise (dB)",
        "col_elec_kwh":      "Electricity (kWh)",
        "col_net_kwh":       "Net kWh",
        "col_kwh_km":        "kWh/km",
        "col_soc":           "SoC %",
        "col_charge_ev":     "Charge Events",
        "col_co2_km":        "CO₂/km (g)",
        "btn_veh_csv":       "⬇️ Download Vehicle Report CSV",
        # EV battery
        "ev_battery":        "### ⚡ EV Battery & Energy Consumption",
        "met_total_cons":    "⚡ Total Consumption",
        "met_net_cons":      "🔋 Net Consumption",
        "met_total_charge":  "🔌 Total Charged",
        "met_avg_soc":       "🔋 Avg. Final SoC",
        "met_perveh_kwh":    "⚡ Per Vehicle",
        "met_avg_kwhkm":     "⚡ Avg. kWh/km",
        "met_min_kwhkm":     "⚡ Min kWh/km",
        "met_max_kwhkm":     "⚡ Max kWh/km",
        "chart_soc":         "**🔋 Final SoC Distribution (%)**",
        "chart_ec":          "**⚡ Consumption Distribution (kWh)**",
        # Fuel vs EV
        "fuel_vs_ev":        "### 🔄 Fuel vs. Electricity Comparison",
        "met_total_fuel":    "⛽ Total Fuel",
        "met_ev_net":        "⚡ EV Net Consumption",
        "met_energy_save":   "🌱 Energy Saving",
        "met_co2_compare":   "💨 CO₂: Fuel → EV",
        "met_less":          "less",
        "methodology":       (
            "**Methodology:**  "
            "Fuel density **820 g/L** (820 000 mg/L, EN 590 diesel).  "
            "SUMO `--emission-output.step-scaled` enabled → each timestep value is already total mg (mg/s × step_s).  "
            "Total fuel = {fuel_mg:,.0f} mg → {fuel_g:,.3f} g → **{fuel_l:,.4f} L** (÷ 820 000).  "
            "1 L diesel ≈ {kwh_per_l} kWh (lower heating value).  "
            "EV CO₂: {ev_kwh:.1f} kWh × 0.45 kg/kWh (Turkey grid factor) = {co2_ev:.1f} kg."
        ),
        "perveh_fuel_ev":    "**Per-vehicle fuel vs. electricity (first 20):**",
        "btn_compare_csv":   "⬇️ Download Comparison CSV",
        "col_rota":          "Route (km)",
        "col_fuel_compare":  "Fuel (g)",
        "col_fuel_l_cmp":    "Fuel (L)",
        "col_elec_cmp":      "Electricity (kWh)",
        # Hourly profile
        "hourly_profile":    "### ⏰ Minute-by-Minute Fuel & CO₂ Profile",
        "chart_fuel_min":    "**⛽ Fuel per Minute (g)**",
        "chart_co2_min":     "**💨 CO₂ per Minute (g)**",
        "col_minute":        "Minute",
        "col_fuel_g2":       "Fuel_g",
        "col_co2_g2":        "CO2_g",
        "readme_title":      "ISTVEL — ISTANBUL TRAFFIC → SUMO PACKAGE",
        "readme_region":     "Region",
        "readme_month":      "Month",
        "readme_hour":       "Hour",
        "readme_all":        "All",
        "readme_fleet":      "Fleet Mode",
        # Comparative analysis tabs
        "tab_ev":            "⚡ EV Fleet",
        "tab_fuel":          "⛽ Fuel Fleet",
        "tab_hybrid":        "🔄 Hybrid Fleet",
        "tab_compare":       "📊 Comparison",
        "cost_settings":     "💰 Cost Parameters",
        "fuel_price":        "⛽ Fuel Price (₺/L)",
        "fuel_price_help":   "Check Shell website for current diesel price",
        "elec_price":        "⚡ Electricity Price (₺/kWh)",
        "elec_price_help":   "ZES DC tariff (as of 07.01.2026: 16.49 ₺/kWh)",
        "no_files":          "📂 No files uploaded for this fleet yet.",
        "fleet_summary":     "### 🏁 Fleet Summary",
        "cost_summary":      "### 💰 Cost Summary",
        "met_fuel_cost":     "💸 Fuel Cost",
        "met_elec_cost":     "💸 Electricity Cost",
        "met_cost_perveh":   "💸 Cost / Vehicle",
        "met_cost_per100km": "💸 Cost / 100 km",
        "compare_title":     "## 🏆 EV / Fuel / Hybrid Comparison",
        "compare_desc":      "Upload files in all three tabs to see the comparison.",
        "compare_energy":    "### ⚡ Energy Consumption",
        "compare_emission":  "### 💨 Emissions",
        "compare_cost":      "### 💰 Total Cost",
        "compare_perveh":    "### 🚗 Per Vehicle",
        "col_fleet":         "Fleet",
        "col_total_cost":    "Total Cost",
        "col_cost_perveh":   "Per Vehicle",
        "col_kwh_total":     "Total kWh",
        "col_fuel_total_l":  "Total Fuel (L)",
        "col_co2_total":     "Total CO₂ (kg)",
        "saving_vs_fuel":    "💚 EV saving vs. Fuel",
        "shell_link":        "🔗 Shell fuel prices",
        "zes_link":          "🔗 ZES pricing",
        "currency_label":    "💱 Currency",
        "tab_cs":            "🔌 Charging Stations",
        "cs_upload_trip":    "📂 Upload chargingstations_output.xml",
        "cs_title":          "### 🔌 Charging Station Analysis",
        "cs_no_data":        "Upload chargingstations_output.xml (SUMO → output/chargingstations_output.xml).",
        "cs_total_charged":  "⚡ Total Charged (kWh)",
        "cs_events":         "🔌 Charging Events",
        "cs_avg_soc_start":  "🔋 Avg. Start SoC",
        "cs_avg_soc_end":    "🔋 Avg. End SoC",
        "cs_cost_per_kwh":   "⚡ Charging Price (unit/kWh)",
        "cs_total_cost":     "💰 Total Charging Cost",
        "cs_vehicles_charged": "🚗 Vehicles Charged",
        "cs_avg_charged_veh": "⚡ Avg. Charged/Vehicle (kWh)",
        "cs_compare_label":  "Charging Stations",
    },
}

# ── Sayfa ayarları ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ISTVEL",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #e0e0e0; }
    section[data-testid="stSidebar"] { background-color: #161b22; }
    h1, h2, h3 { color: #f0a030 !important; }
    .sumo-box {
        background: linear-gradient(135deg, rgba(30,60,30,0.4), rgba(20,40,20,0.2));
        border: 1px solid rgba(46,204,113,0.3);
        border-radius: 12px;
        padding: 20px;
        margin-top: 20px;
    }
    /* Fleet mode buttons */
    .fleet-btn-ev   { background:#1a472a !important; border:2px solid #2ecc71 !important; }
    .fleet-btn-fuel { background:#4a1a1a !important; border:2px solid #e74c3c !important; }
    .fleet-btn-hyb  { background:#2a2a4a !important; border:2px solid #3498db !important; }
    /* Manual point badge */
    .point-badge {
        display:inline-block; background:#f0a030; color:#000;
        border-radius:50%; width:24px; height:24px;
        text-align:center; line-height:24px; font-weight:bold;
        margin:2px;
    }
</style>
""", unsafe_allow_html=True)

# ── Bölge tanımları ────────────────────────────────────────────────────────
BOLGE_TANIMLARI = {
    "Kadıköy":   {"place": "Kadıköy, Istanbul, Turkey",
                  "bbox": (40.970, 40.995, 29.050, 29.090)},
    "Beşiktaş":  {"place": "Beşiktaş, Istanbul, Turkey",
                  "bbox": (41.038, 41.058, 29.000, 29.030)},
    "Şişli":     {"place": "Şişli, Istanbul, Turkey",
                  "bbox": (41.052, 41.075, 28.975, 29.010)},
    "Üsküdar":   {"place": "Üsküdar, Istanbul, Turkey",
                  "bbox": (41.010, 41.040, 29.010, 29.060)},
    "Fatih":     {"place": "Fatih, Istanbul, Turkey",
                  "bbox": (41.000, 41.025, 28.920, 28.970)},
    "Tüm İstanbul": {"place": None,
                     "bbox": (40.850, 41.200, 28.500, 29.500)},
}

# ── Resource ID listesi ────────────────────────────────────────────────────
RESOURCES = {
    "Ocak 2020":    "db9c7fb3-e7f9-435a-92f4-1b917e357821",
    "Şubat 2020":   "5fb30ee1-e079-4865-a8cd-16efe2be8352",
    "Mart 2020":    "efff9df8-4f40-4a46-8c99-2b3b4c5e2b8c",
    "Nisan 2020":   "9ead7895-27fb-4aed-847f-ffe1504c36fa",
    "Mayıs 2020":   "5c0da73a-2fd6-4f98-90fe-aa32ce98b607",
    "Haziran 2020": "62099013-e557-4d23-a2c0-70f7ee89c3b9",
    "Temmuz 2020":  "e5fb99b3-afa0-4a9d-9bc8-cf98940da082",
    "Ağustos 2020": "dc40309d-7fd6-43e2-ad85-5db9db133a5b",
    "Eylül 2020":   "ef34bd55-86d8-4459-a710-79de30a45be2",
    "Ekim 2020":    "949d4a3b-91d2-4c56-b82f-4ef081e39c45",
    "Kasım 2020":   "93f996f1-70da-4500-951a-693c7e7066f6",
    "Aralık 2020":  "3e3161d8-7668-4694-829c-9179b41a775b",
    "Ocak 2021":    "fb7094a3-cf2f-46a6-996a-f6a9c5f3b9be",
    "Şubat 2021":   "395811ac-4152-4e04-88ef-8d4e30e6ac17",
    "Mart 2021":    "fdbc8e2f-0cf1-4952-b50f-df8f40d5a649",
    "Nisan 2021":   "1eb158e8-8da7-4572-9825-108714a8856e",
    "Mayıs 2021":   "00d72836-d035-462d-a66e-408883216195",
    "Haziran 2021": "936faaf6-45ed-4463-ac57-85658c745cdc",
    "Temmuz 2021":  "dde8cd53-f6aa-443e-916e-ab62a75be9a1",
    "Ağustos 2021": "345b86b6-15ea-4416-831a-478f0d6f9b19",
    "Eylül 2021":   "2bd92b0f-cbee-4cfb-9e94-c74b30c80fa2",
    "Ekim 2021":    "431bdb72-2204-4032-a96a-a810a2e88a0f",
    "Kasım 2021":   "b9131a98-99eb-4870-8960-e5f58f82e350",
    "Aralık 2021":  "2536eb25-9129-41e3-a028-f8a71fb16561",
    "Ocak 2022":    "8f492f69-95d0-46d7-b265-c141f8dba1a2",
    "Şubat 2022":   "7f655821-af63-4ba7-b3fe-9255a42ccff6",
    "Mart 2022":    "3b7047b3-5b13-41c6-81d4-5dcf5c8c3696",
    "Nisan 2022":   "d57f1256-a0a5-4265-83b4-e06ee0458f49",
    "Mayıs 2022":   "a250bd0a-ef49-4daf-a861-5a616056a9f4",
    "Haziran 2022": "21a42752-4189-44fe-89ae-f17944f53a69",
    "Temmuz 2022":  "287e7fc9-6d92-4019-ac58-ff6bca6e6151",
    "Ağustos 2022": "acd85951-6d23-4b50-bac6-d941f92af1ad",
    "Eylül 2022":   "a5da03fe-4a89-493b-ae60-aeb132511be9",
    "Ekim 2022":    "72183a60-d47f-4dc9-b1dc-fced0649dcf5",
    "Kasım 2022":   "7f463362-a580-41d9-a86a-a542818e7542",
    "Aralık 2022":  "dc788908-2b75-434f-9f3f-ef82ff33a158",
    "Ocak 2023":    "42fa7a5f-29f1-4b38-9dfa-ac7c8fe3c77d",
    "Şubat 2023":   "366befd8-defd-4f79-a3d2-0e7948c649ff",
    "Mart 2023":    "6a60b03a-bf25-4575-9dce-e21fe0e04e77",
    "Nisan 2023":   "ce65562e-0d17-4d7e-8090-9484990a8f2b",
    "Mayıs 2023":   "d0a71c11-47d2-4f98-8745-c9446b10bf18",
    "Haziran 2023": "a99913df-dccc-4b7d-b6e3-963ccb5d27b1",
    "Temmuz 2023":  "3de18c1e-57c0-4493-9b75-5a896edae0ff",
    "Ağustos 2023": "f6a1e2d7-0d9f-4d84-90c6-2729a0869308",
    "Eylül 2023":   "7b9a35a7-dc9c-4044-b117-1c0003104630",
    "Ekim 2023":    "342488a2-a00f-4ba7-bb4a-345f75f1120d",
    "Kasım 2023":   "e6a18077-2bd9-4201-8d4a-5398b0e2d99c",
    "Aralık 2023":  "aa58374d-ef6f-411f-8271-5b63eefe4fde",
    "Ocak 2024":    "7d9cbf11-f4b8-464d-bb3a-642b79e8b32b",
    "Şubat 2024":   "601cd734-9a62-44e0-89e5-bbfc2161d389",
    "Mart 2024":    "b67e9415-0ba8-4319-8d36-359240a93808",
    "Nisan 2024":   "0c7d60f3-8349-4836-a1c2-56ec93cbbd50",
    "Mayıs 2024":   "674604c8-8d08-42ff-a0b3-e2bde9f39455",
    "Haziran 2024": "674ba2c5-76b0-4f24-8e17-9aa2071d2572",
    "Temmuz 2024":  "0019216e-48e0-4cec-9ab8-93d67f66dac3",
    "Ağustos 2024": "168467fe-0495-4cdf-a93a-7c1e91179457",
    "Eylül 2024":   "914cb0b9-d941-4408-98eb-f378519c26f4",
    "Ekim 2024":    "d291989c-429d-4e61-9c70-1f76294b96b8",
    "Kasım 2024":   "bedd5ab2-9a00-4966-9921-9672d4478a51",
    "Aralık 2024":  "76671ebe-2fd2-426f-b85a-e3772263f483",
    "Ocak 2025":    "57cb067b-1a0b-460b-8342-7884bd4537e8",
}

# Türkçe → İngilizce ay adı çevirisi
MONTH_TR_TO_EN = {
    "Ocak": "January", "Şubat": "February", "Mart": "March",
    "Nisan": "April",  "Mayıs": "May",       "Haziran": "June",
    "Temmuz": "July",  "Ağustos": "August",  "Eylül": "September",
    "Ekim": "October", "Kasım": "November",  "Aralık": "December",
}

def tr_to_en_month(tr_label: str) -> str:
    """'Ocak 2022' → 'January 2022'"""
    parts = tr_label.split()
    if len(parts) == 2:
        return f"{MONTH_TR_TO_EN.get(parts[0], parts[0])} {parts[1]}"
    return tr_label

def en_to_tr_month(en_label: str) -> str:
    """'January 2022' → 'Ocak 2022'  (RESOURCES key'i için)"""
    EN_TO_TR = {v: k for k, v in MONTH_TR_TO_EN.items()}
    parts = en_label.split()
    if len(parts) == 2:
        return f"{EN_TO_TR.get(parts[0], parts[0])} {parts[1]}"
    return en_label

API_BASE = "https://data.ibb.gov.tr/api/3/action/datastore_search"
SQL_BASE = "https://data.ibb.gov.tr/api/3/action/datastore_search_sql"


# ══════════════════════════════════════════════════════════════════════════════
#  VERİ ÇEKME
# ══════════════════════════════════════════════════════════════════════════════

@st.cache_data(ttl=600, show_spinner=False)
def _fetch_pages(resource_id: str, sql_filter: str, fetch_limit: int) -> list:
    all_records = []
    offset = 0
    batch = 5000

    while len(all_records) < fetch_limit:
        if sql_filter:
            sql = f"""SELECT * FROM "{resource_id}" {sql_filter} LIMIT {batch} OFFSET {offset}"""
            resp = requests.get(SQL_BASE, params={"sql": sql}, timeout=60)
        else:
            resp = requests.get(
                API_BASE,
                params={"resource_id": resource_id, "limit": batch, "offset": offset},
                timeout=60,
            )
        resp.raise_for_status()
        data = resp.json()
        if not data.get("success"):
            raise ValueError(data.get("error", {}).get("message", "API error"))

        records = data["result"]["records"]
        if not records:
            break

        all_records.extend(records)
        offset += len(records)

        if not sql_filter:
            if len(all_records) >= data["result"].get("total", fetch_limit):
                break
        if len(records) < batch:
            break

    return all_records


def _to_df(records: list) -> pd.DataFrame:
    if not records:
        return pd.DataFrame()
    df = pd.DataFrame(records)
    for col in ["LATITUDE", "LONGITUDE", "MINIMUM_SPEED", "MAXIMUM_SPEED",
                "AVERAGE_SPEED", "NUMBER_OF_VEHICLES"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["LATITUDE", "LONGITUDE"])
    if "DATE_TIME" in df.columns:
        df["_dt"]   = pd.to_datetime(df["DATE_TIME"], errors="coerce")
        df["_hour"] = df["_dt"].dt.hour
        df["_day"]  = df["_dt"].dt.day
    return df.reset_index(drop=True)


def fetch_data(resource_id, hour, day, limit=50000):
    filters = []
    if day is not None:
        filters.append(f""""DATE_TIME" LIKE '%-{str(day).zfill(2)} %'""")
    if hour is not None:
        filters.append(f""""DATE_TIME" LIKE '% {str(hour).zfill(2)}:%'""")
    sql_filter = ("WHERE " + " AND ".join(filters)) if filters else ""

    bar = st.progress(0, text="📡 Fetching data from API…")
    try:
        records = _fetch_pages(resource_id, sql_filter, limit)
        bar.progress(90, text=f"🔧 Processing {len(records):,} records…")
        df = _to_df(records)
        bar.empty()
        return df
    except Exception:
        bar.empty()
        raise


# ══════════════════════════════════════════════════════════════════════════════
#  SUMO EXPORT FONKSİYONLARI
# ══════════════════════════════════════════════════════════════════════════════

def bbox_filtrele(df: pd.DataFrame, bbox: tuple) -> pd.DataFrame:
    """Returns rows within bounding box: (min_lat, max_lat, min_lon, max_lon)"""
    min_lat, max_lat, min_lon, max_lon = bbox
    mask = (
        (df["LATITUDE"]  >= min_lat) & (df["LATITUDE"]  <= max_lat) &
        (df["LONGITUDE"] >= min_lon) & (df["LONGITUDE"] <= max_lon)
    )
    return df[mask].copy()


@st.cache_data(ttl=3600, show_spinner=False)
def osm_ag_cek(place_name: str):
    """Fetches OSM road network via osmnx."""
    G = ox.graph_from_place(place_name, network_type="drive")
    G = ox.add_edge_speeds(G)
    G = ox.add_edge_travel_times(G)
    return G


def nearest_edge_snap(G, df: pd.DataFrame):
    """
    Snaps each IMM point to the nearest OSM edge.
    Returns: df + ['edge_u', 'edge_v', 'edge_key'] columns
    """
    lats = df["LATITUDE"].values
    lons = df["LONGITUDE"].values
    results = ox.nearest_edges(G, lons, lats, return_dist=True)
    # results = (edges, distances)
    edges, dists = results
    df = df.copy()
    df["edge_u"]    = [e[0] for e in edges]
    df["edge_v"]    = [e[1] for e in edges]
    df["edge_key"]  = [e[2] for e in edges]
    df["snap_dist"] = dists
    return df


def edge_ozeti_hesapla(df_snap: pd.DataFrame) -> pd.DataFrame:
    """
    Summarizes snapped data per edge.
    Per edge: total vehicles, avg speed, min/max speed.
    """
    grp = df_snap.groupby(["edge_u", "edge_v", "edge_key"]).agg(
        total_vehicles = ("NUMBER_OF_VEHICLES", "sum"),
        avg_speed      = ("AVERAGE_SPEED",      "mean"),
        min_speed      = ("MINIMUM_SPEED",       "min"),
        max_speed      = ("MAXIMUM_SPEED",       "max"),
        sample_count   = ("NUMBER_OF_VEHICLES",  "count"),
    ).reset_index()
    return grp


def edgedata_xml_uret(edge_ozet: pd.DataFrame, saat: int | None, gun: int | None) -> str:
    """
    Generates SUMO edgeData XML format.
    SUMO bunu trafficState veya meanData olarak okuyabilir.
    """
    begin = f"{saat}:00:00" if saat is not None else "0:00:00"
    end   = f"{saat+1}:00:00" if saat is not None else "24:00:00"

    root = ET.Element("meandata")
    interval = ET.SubElement(root, "interval",
                             begin=begin, end=end, id="ibb_traffic")

    for _, row in edge_ozet.iterrows():
        edge_id = f"{int(row['edge_u'])}_{int(row['edge_v'])}_{int(row['edge_key'])}"
        ET.SubElement(interval, "edge",
                      id=edge_id,
                      speed=f"{row['avg_speed']:.2f}",
                      departed=str(int(row['total_vehicles'])),
                      sampledSeconds=f"{row['sample_count'] * 3600:.1f}")

    raw = ET.tostring(root, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def osm_xml_uret(G) -> str:
    """Returns osmnx graph in OSM XML format (for netconvert)."""
    with tempfile.NamedTemporaryFile(suffix=".osm", delete=False, mode="w") as f:
        ox.save_graph_xml(G, filepath=f.name)
        return f.name


def sumo_net_xml_uret(osm_path: str, output_dir: str) -> tuple[bool, str]:
    """
    Converts .osm → .net.xml using netconvert.
    SUMO_HOME environment variable must be set.
    """
    net_path = os.path.join(output_dir, "network.net.xml")
    sumo_home = os.environ.get("SUMO_HOME", "")

    # Olası netconvert yolları
    candidates = [
        "netconvert",
        os.path.join(sumo_home, "bin", "netconvert"),
        "/usr/share/sumo/bin/netconvert",
        "C:/Program Files (x86)/Eclipse/Sumo/bin/netconvert.exe",
        "C:/Program Files/Eclipse/Sumo/bin/netconvert.exe",
    ]

    netconvert_cmd = None
    sumo_home_found = sumo_home

    # SUMO_HOME yoksa yaygın macOS/Linux/Windows yollarını tara
    if not sumo_home_found:
        mac_paths = [
            "/usr/local/share/sumo",   # macOS brew (correct path)
            "/usr/local/opt/sumo",
            "/opt/homebrew/opt/sumo",
            "/opt/homebrew/share/sumo",
            os.path.expanduser("~/sumo"),
            "/usr/share/sumo",
        ]
        win_paths = [
            "C:/Program Files (x86)/Eclipse/Sumo",
            "C:/Program Files/Eclipse/Sumo",
        ]
        for p in mac_paths + win_paths:
            if os.path.isdir(p):
                sumo_home_found = p
                break

    for c in candidates:
        try:
            result = subprocess.run([c, "--version"],
                                    capture_output=True, timeout=5)
            if result.returncode == 0:
                netconvert_cmd = c
                break
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue

    if netconvert_cmd is None:
        return False, "netconvert not found. Check your SUMO_HOME environment variable."

    # typemap dosyasını bul
    typemap_candidates = []
    if sumo_home_found:
        typemap_candidates.append(
            os.path.join(sumo_home_found, "data", "typemap", "osmNetconvert.typ.xml")
        )
    # pip ile kurulan sumo paketi
    try:
        import sumo
        typemap_candidates.append(
            os.path.join(os.path.dirname(sumo.__file__), "data", "typemap", "osmNetconvert.typ.xml")
        )
    except ImportError:
        pass

    typemap_arg = []
    for tm in typemap_candidates:
        if os.path.isfile(tm):
            typemap_arg = ["--type-files", tm]
            break

    cmd = [
        netconvert_cmd,
        "--osm-files", osm_path,
        "--output-file", net_path,
        "--geometry.remove",
        "--roundabouts.guess",
        "--ramps.guess",
        "--junctions.join",
        "--tls.guess-signals",
        "--tls.discard-simple",
        "--no-warnings",
    ] + typemap_arg
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        return False, result.stderr[:1000]
    return True, net_path


def sumo_cfg_uret(output_dir: str, saat: int | None, cs_enabled: bool = False) -> str:
    """Generates SUMO .sumocfg configuration file."""
    begin = saat * 3600 if saat is not None else 0
    end   = begin + 3600

    cfg_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<configuration>
    <input>
        <net-file value="network.net.xml"/>
        <route-files value="routes.rou.xml"/>
        <additional-files value="edgedata.add.xml{',charging_stations.add.xml' if cs_enabled else ''}"/>
    </input>
    <time>
        <begin value="{begin}"/>
        <end value="{end}"/>
        <step-length value="1"/>
    </time>
    <o>
        <summary-output value="output/summary.xml"/>
        <tripinfo-output value="output/tripinfo.xml"/>
        <tripinfo-output.write-unfinished value="true"/>
        <emission-output value="output/emission.xml"/>
        <emission-output.precision value="2"/>
        <emission-output.step-scaled value="true"/>
{f'        <chargingstations-output value="output/chargingstations_output.xml"/>\n' if cs_enabled else ''}
    </o>
    <processing>
        <ignore-route-errors value="true"/>
        <max-depart-delay value="120"/>
        <time-to-teleport value="300"/>
        <time-to-teleport.highways value="60"/>
        <lanechange.duration value="3"/>
        <collision.action value="teleport"/>
        <collision.mingap-factor value="0"/>
        <emergencydecel.warning-threshold value="1"/>
        <random-depart-offset value="30"/>
        <routing-algorithm value="dijkstra"/>
        <device.emissions.period value="30"/>
    </processing>
    <report>
        <no-step-log value="true"/>
        <no-warnings value="false"/>
    </report>
</configuration>"""

    os.makedirs(os.path.join(output_dir, "output"), exist_ok=True)
    path = os.path.join(output_dir, "simulation.sumocfg")
    with open(path, "w") as f:
        f.write(cfg_content)
    return path


def edgedata_additional_xml_uret(output_dir: str) -> str:
    """Generates SUMO edgeData additional file (edgedata.add.xml)."""
    content = """<?xml version="1.0" encoding="UTF-8"?>
<additional>
    <edgeData id="ibb_meandata" file="edgedata_output.xml" period="3600"/>
</additional>"""
    path = os.path.join(output_dir, "edgedata.add.xml")
    with open(path, "w") as f:
        f.write(content)
    return path


def net_xml_edge_map_olustur(net_xml_path: str) -> dict[tuple[str,str], str]:
    """
    Builds (from_node, to_node) → edge_id mapping from net.xml.
    netconvert uses its own sequential IDs but from/to node IDs
    match OSM node IDs — enabling osmnx-based matching.
    """
    mapping: dict[tuple[str,str], str] = {}
    if not net_xml_path or not os.path.isfile(net_xml_path):
        return mapping
    try:
        tree = ET.parse(net_xml_path)
        for edge_el in tree.getroot().findall("edge"):
            eid  = edge_el.get("id", "")
            frm  = edge_el.get("from", "")
            to   = edge_el.get("to", "")
            if eid.startswith(":") or not frm or not to:
                continue
            mapping[(frm, to)] = eid
    except Exception:
        pass
    return mapping


def hiz_rengi(avg_spd_ms: float) -> str:
    """Returns SUMO GUI color (R,G,B,A) string based on speed."""
    kmh = avg_spd_ms * 3.6
    if kmh >= 60:
        return "0,200,80,255"
    elif kmh >= 30:
        return "255,160,0,255"
    else:
        return "220,40,40,255"


def vehicles_xml_uret(edge_ozet: pd.DataFrame, G, net_xml_path: str | None,
                      saat: int | None,
                      fleet_mode: str = "EV",
                      hybrid_ev_ratio: float = 0.40) -> str:
    """
    Generates SUMO <vehicle>+<route> XML.

    Kritik fark: adjacency <connection> elementlerinden kurulur (edge→edge).
    BFS only uses real connections SUMO knows →
    reduces 'no connection between edge A and edge B' errors and teleports.
    """
    import random
    from collections import deque

    master_seed = int(time.time() * 1000) % (2**31)
    rng = random.Random(master_seed)

    begin_s  = (saat * 3600) if saat is not None else 0
    end_s    = begin_s + 3600
    interval = end_s - begin_s

    # ── net.xml parse: edge metadata + connection-based adjacency ─────────────
    edge_len:   dict[str, float]       = {}   # eid → length_m
    edge_from:  dict[str, str]         = {}   # eid → from_node
    uv_to_edge: dict[tuple, str]       = {}   # (u,v) → eid
    all_edges:  list[str]              = []
    # edge→edge adjacency (SUMO connection elementlerinden)
    conn_adj:   dict[str, list[str]]   = {}   # from_edge → [to_edge, ...]

    if net_xml_path and os.path.isfile(net_xml_path):
        try:
            tree = ET.parse(net_xml_path)
            root_net = tree.getroot()

            # 1) Edge metadata
            for el in root_net.findall("edge"):
                eid = el.get("id", "")
                frm = el.get("from", "")
                to  = el.get("to",  "")
                if not eid or eid.startswith(":") or not frm or not to:
                    continue
                lanes = el.findall("lane")
                if not lanes:
                    continue
                try:
                    length = float(lanes[0].get("length", 0))
                except (ValueError, TypeError):
                    length = 0.0
                if length < 5:
                    continue
                edge_len[eid]       = length
                edge_from[eid]      = frm
                uv_to_edge[(frm,to)] = eid
                all_edges.append(eid)
                conn_adj[eid] = []   # initially empty

            # 2) Connection-based adjacency (en önemli kısım)
            for el in root_net.findall("connection"):
                frm_e = el.get("from", "")
                to_e  = el.get("to",   "")
                # internal edge'leri atla
                if not frm_e or not to_e:
                    continue
                if frm_e.startswith(":") or to_e.startswith(":"):
                    continue
                if frm_e in conn_adj and to_e in edge_len:
                    if to_e not in conn_adj[frm_e]:
                        conn_adj[frm_e].append(to_e)

        except Exception:
            pass

    if not all_edges:
        return "<!-- net.xml could not be read -->"

    # Bağlantısı olan edge'leri filtrele (çıkış yolu olan)
    reachable_starts = [e for e in all_edges if conn_adj.get(e)]
    if not reachable_starts:
        reachable_starts = all_edges

    # ── BFS: edge→edge (connection tabanlı) ──────────────────────────────────
    def bfs_edge(src_edge: str, min_hops: int, rng_local) -> list[str]:
        """
        BFS from src_edge over conn_adj.
        Returns first route with at least min_hops edge transitions.
        Target chosen randomly — tries to reach a distant edge.
        """
        if src_edge not in conn_adj or not conn_adj[src_edge]:
            return []

        # Pick a random distant target (one with conn_adj entry)
        candidates = [e for e in reachable_starts if e != src_edge]
        if not candidates:
            return []
        dst_edge = rng_local.choice(candidates)

        queue   = deque([(src_edge, [src_edge])])
        visited = {src_edge}
        best    = []

        while queue:
            cur, path = queue.popleft()
            if cur == dst_edge and len(path) >= min_hops:
                return path
            if len(path) > min_hops * 3:   # max depth limit
                if len(path) > len(best):
                    best = path
                continue
            nexts = conn_adj.get(cur, [])
            shuffled = nexts[:]
            rng_local.shuffle(shuffled)
            for nxt in shuffled:
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, path + [nxt]))

        return best if len(best) >= 2 else []

    # ── IBB ağırlıkları ───────────────────────────────────────────────────────
    ibb_weights: dict[str, int] = {}
    for _, row in edge_ozet.iterrows():
        u   = str(int(row["edge_u"]))
        v   = str(int(row["edge_v"]))
        n   = max(1, int(row["total_vehicles"]))
        eid = uv_to_edge.get((u,v)) or uv_to_edge.get((v,u))
        if eid and eid in edge_len and conn_adj.get(eid):
            ibb_weights[eid] = ibb_weights.get(eid,0) + n

    # Departure pool: only edges with outgoing connections
    pool_edges   = []
    pool_weights = []
    for eid in reachable_starts:
        w = ibb_weights.get(eid, 0)
        pool_edges.append(eid)
        pool_weights.append(max(1, w * 5))

    # ── vType tanımları ───────────────────────────────────────────────────────
    root_el = ET.Element("routes")

    if fleet_mode in ("EV", "HYBRID"):
        vtype_ev = ET.SubElement(root_el, "vType",
                      id="evCar",
                      minGap="2.50", maxSpeed="29.06",
                      accel="2.6",  decel="4.5",
                      sigma="0.8",
                      speedFactor="normc(1,0.15,0.5,1.5)",
                      length="4.6",
                      emissionClass="Energy/unknown",
                      mass="1830",
                      guiShape="passenger")
        for k, v in [
            ("has.battery.device",      "true"),
            ("airDragCoefficient",      "0.35"),
            ("constantPowerIntake",     "100"),
            ("frontSurfaceArea",        "2.6"),
            ("rotatingMass",            "40"),
            ("device.battery.capacity", "64000"),
            ("maximumPower",            "150000"),
            ("propulsionEfficiency",    "0.98"),
            ("radialDragCoefficient",   "0.1"),
            ("recuperationEfficiency",  "0.96"),
            ("rollDragCoefficient",     "0.01"),
            ("stoppingThreshold",       "0.1"),
        ]:
            ET.SubElement(vtype_ev, "param", key=k, value=v)

    if fleet_mode in ("FUEL", "HYBRID"):
        ET.SubElement(root_el, "vType",
                      id="fuelCar",
                      minGap="2.50", maxSpeed="33.33",
                      accel="2.9",  decel="4.5",
                      sigma="0.8",
                      speedFactor="normc(1,0.15,0.5,1.5)",
                      length="4.5",
                      emissionClass="HBEFA3/PC_D_EU4",
                      guiShape="passenger",
                      color="200,80,80,255")

    # ── Araç üretimi ──────────────────────────────────────────────────────────
    total_vehicles = max(1, int(edge_ozet["total_vehicles"].sum()))
    MIN_HOPS  = 6    # at least 6 edge transitions (~300-600m)
    MAX_TRIES = 4

    slot    = interval / total_vehicles
    matched = 0
    skipped = 0

    for i in range(total_vehicles):
        veh_rng = random.Random(master_seed ^ (i * 2654435761))

        # Departure edge (from pool with connections)
        from_edge = veh_rng.choices(pool_edges, weights=pool_weights, k=1)[0]

        # BFS rotası — birkaç deneme
        route_edges = []
        for _try in range(MAX_TRIES):
            r = bfs_edge(from_edge, MIN_HOPS, veh_rng)
            if len(r) >= MIN_HOPS:
                route_edges = r
                break
            if r and len(r) > len(route_edges):
                route_edges = r

        if len(route_edges) < 2:
            skipped += 1
            continue

        # Depart zamanı
        depart = begin_s + i * slot + rng.uniform(0, slot * 0.8)
        depart = max(begin_s + 0.1, depart)

        # Araç tipi
        if fleet_mode == "EV":
            vtype_id = "evCar";   color = "0,180,80,255"
        elif fleet_mode == "FUEL":
            vtype_id = "fuelCar"; color = "200,80,80,255"
        else:
            if (i % 100) < int(hybrid_ev_ratio * 100):
                vtype_id = "evCar";   color = "0,180,80,255"
            else:
                vtype_id = "fuelCar"; color = "200,80,80,255"

        # IBB hızı
        ibb_row = edge_ozet[
            edge_ozet.apply(lambda r:
                uv_to_edge.get((str(int(r["edge_u"])), str(int(r["edge_v"])))) == from_edge
                or uv_to_edge.get((str(int(r["edge_v"])), str(int(r["edge_u"])))) == from_edge,
                axis=1)
        ]
        spd_kmh = float(ibb_row.iloc[0]["avg_speed"]) if not ibb_row.empty else 30.0
        dept_spd = f"{max(1.0, spd_kmh / 3.6):.2f}"

        veh_el = ET.SubElement(root_el, "vehicle",
                               id=f"veh_{i}",
                               type=vtype_id,
                               depart=f"{depart:.1f}",
                               departLane="best",
                               departSpeed=dept_spd,
                               arrivalLane="current",
                               arrivalSpeed="current",
                               color=color)
        ET.SubElement(veh_el, "route", edges=" ".join(route_edges))
        matched += 1

    comment = ET.Comment(
        f" connection-BFS | {total_vehicles} target | {matched} generated | "
        f"{skipped} skipped | min_hops={MIN_HOPS} | seed={master_seed} "
    )
    root_el.insert(0, comment)

    raw = ET.tostring(root_el, encoding="unicode")
    return minidom.parseString(raw).toprettyxml(indent="  ")


def charging_stations_xml_uret(net_xml_path: str,
                               aralik_km: float = 1.0,
                               guc_kw: float = 50.0,
                               verim: float = 0.95,
                               transit_sarj: bool = True,
                               boy_m: float = 10.0,
                               delay: int = 0) -> str:
    """
    Assigns charging stations to edges in net.xml at regular intervals.

    aralik_km  : Minimum spacing between stations (km)
    guc_kw     : Charging power (kW) → SUMO expects Watts
    verim      : Charging efficiency (0-1)
    transit_sarj: Charge while moving (chargeInTransit)

    Checks each edge length; adds station to edges longer than aralik_km.
    Short edges are skipped (avoids clustering).
    """
    if not net_xml_path or not os.path.isfile(net_xml_path):
        return ""

    aralik_m   = aralik_km * 1000
    guc_w      = int(guc_kw * 1000)
    transit    = "1" if transit_sarj else "0"

    root = ET.Element("additional")
    cs_count = 0

    try:
        tree = ET.parse(net_xml_path)
        for edge_el in tree.getroot().findall("edge"):
            eid  = edge_el.get("id", "")
            if eid.startswith(":"):
                continue

            # Edge uzunluğunu lane'den al
            lanes = edge_el.findall("lane")
            if not lanes:
                continue
            try:
                edge_len = float(lanes[0].get("length", 0))
            except (ValueError, TypeError):
                continue

            if edge_len < aralik_m * 0.3:   # skip very short edges
                continue

            lane_id  = f"{eid}_0"
            half     = boy_m / 2.0
            pos      = aralik_m / 2   # first station near edge midpoint
            idx      = 0
            while pos < edge_len - half:
                cs_id    = f"cs_{eid}_{idx}"
                start_p  = max(0.0, pos - half)
                end_p    = min(edge_len - 0.1, pos + half)
                ET.SubElement(root, "chargingStation",
                              id=cs_id,
                              lane=lane_id,
                              startPos=f"{start_p:.1f}",
                              endPos=f"{end_p:.1f}",
                              power=str(guc_w),
                              efficiency=str(verim),
                              chargeInTransit=transit,
                              chargeDelay=str(delay))
                cs_count += 1
                pos      += aralik_m
                idx      += 1

    except Exception as e:
        ET.SubElement(root, ET.Comment(f" Error: {e} "))

    raw = ET.tostring(root, encoding="unicode")
    xml_str = minidom.parseString(raw).toprettyxml(indent="  ")
    return xml_str


def zip_olarak_paketle(dosyalar: dict) -> bytes:
    """
    files: {filename: content_string or file_path}
    Returns ZIP bytes.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for isim, icerik in dosyalar.items():
            if isinstance(icerik, str) and os.path.isfile(icerik):
                zf.write(icerik, isim)
            else:
                zf.writestr(isim, icerik)
    return buf.getvalue()


def dogrulama_haritasi_olustur(df_orijinal: pd.DataFrame,
                                df_snap: pd.DataFrame,
                                edge_ozet: pd.DataFrame,
                                G) -> folium.Map:
    """
    Validation map showing IMM points + snap lines + busiest edges.
    """
    center = [df_orijinal["LATITUDE"].mean(), df_orijinal["LONGITUDE"].mean()]
    m = folium.Map(location=center, zoom_start=14, tiles="CartoDB dark_matter")

    # En yoğun 20 edge'i vurgula
    top_edges = edge_ozet.nlargest(20, "total_vehicles")
    for _, row in top_edges.iterrows():
        u, v, k = int(row["edge_u"]), int(row["edge_v"]), int(row["edge_key"])
        if u in G.nodes and v in G.nodes:
            u_data = G.nodes[u]
            v_data = G.nodes[v]
            locs = [[u_data["y"], u_data["x"]], [v_data["y"], v_data["x"]]]
            intensity = min(row["total_vehicles"] / edge_ozet["total_vehicles"].max(), 1.0)
            r = int(220 * intensity)
            g = int(60 + 140 * (1 - intensity))
            color = f"#{r:02x}{g:02x}3c"
            folium.PolyLine(
                locs, color=color, weight=4 + intensity * 6,
                opacity=0.85,
                tooltip=f"Vehicles: {int(row['total_vehicles'])} | Speed: {row['avg_speed']:.1f} km/h"
            ).add_to(m)

    # İBB noktaları (küçük)
    for _, row in df_snap.head(500).iterrows():
        folium.CircleMarker(
            location=[row["LATITUDE"], row["LONGITUDE"]],
            radius=3,
            color="#4af",
            fill=True,
            fill_opacity=0.6,
            weight=0,
            tooltip=f"Geohash: {row.get('GEOHASH','?')} | Snap dist: {row['snap_dist']:.1f}m"
        ).add_to(m)

    return m


# ══════════════════════════════════════════════════════════════════════════════
#  HARITA (FAZ 1)
# ══════════════════════════════════════════════════════════════════════════════

def speed_to_color(avg_speed):
    if pd.isna(avg_speed):
        return "#666666"
    if avg_speed >= 60:
        return "#2ecc71"
    elif avg_speed >= 30:
        return "#f39c12"
    return "#e74c3c"


def fmt_spd(v) -> str:
    """Safely converts a speed value to a string."""
    try:
        f = float(v)
        return f"{f:.1f}" if not pd.isna(f) else "?"
    except (TypeError, ValueError):
        return "?"


def build_map(df: pd.DataFrame, view_mode: str, L: dict) -> folium.Map:
    center_lat = df["LATITUDE"].mean()
    center_lon = df["LONGITUDE"].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=11,
                   tiles="CartoDB dark_matter", prefer_canvas=True)

    # Dil-bağımsız mod karşılaştırması: mevcut L string'iyle eşleştir
    is_heat    = view_mode == L["viz_heat"]
    is_circle  = view_mode == L["viz_circle"]
    is_cluster = view_mode == L["viz_cluster"]

    if is_heat:
        heat_data = []
        for _, r in df.iterrows():
            try:
                v = float(r["NUMBER_OF_VEHICLES"]) if r["NUMBER_OF_VEHICLES"] else 1
                heat_data.append([r["LATITUDE"], r["LONGITUDE"], v])
            except (TypeError, ValueError):
                heat_data.append([r["LATITUDE"], r["LONGITUDE"], 1])
        HeatMap(heat_data, radius=18, blur=12, max_zoom=13,
                gradient={0.2: "#1a1aff", 0.5: "#f0a030", 0.8: "#ff0000"}).add_to(m)

    elif is_circle:
        for _, row in df.iterrows():
            try:
                vehicles = float(row.get("NUMBER_OF_VEHICLES") or 1)
            except (TypeError, ValueError):
                vehicles = 1
            avg_spd = row.get("AVERAGE_SPEED", None)
            color   = speed_to_color(avg_spd)
            popup_html = (
                f"<b>Geohash:</b> {row.get('GEOHASH','?')}<br>"
                f"<b>{L['popup_datetime']}:</b> {row.get('DATE_TIME','?')}<br>"
                f"<b>{L['popup_vehicles']}:</b> {int(vehicles)}<br>"
                f"<b>{L['popup_avg_speed']}:</b> {fmt_spd(avg_spd)} km/h<br>"
                f"<b>{L['popup_minmax']}:</b> {fmt_spd(row.get('MINIMUM_SPEED'))} / {fmt_spd(row.get('MAXIMUM_SPEED'))} km/h"
            )
            folium.CircleMarker(
                location=[row["LATITUDE"], row["LONGITUDE"]],
                radius=max(4, min(int(np.sqrt(vehicles) * 0.8), 20)),
                color=color, fill=True, fill_color=color,
                fill_opacity=0.7, weight=1,
                popup=folium.Popup(popup_html, max_width=240),
            ).add_to(m)

    elif is_cluster:
        cluster = MarkerCluster().add_to(m)
        for _, row in df.iterrows():
            avg_spd = row.get("AVERAGE_SPEED", None)
            try:
                v = int(float(row.get("NUMBER_OF_VEHICLES") or 0))
            except (TypeError, ValueError):
                v = 0
            folium.CircleMarker(
                location=[row["LATITUDE"], row["LONGITUDE"]],
                radius=6, color=speed_to_color(avg_spd),
                fill=True, fill_opacity=0.8, weight=0,
                popup=f"{L['popup_vehicles']}: {v} | {L['popup_avg_speed']}: {fmt_spd(avg_spd)} km/h",
            ).add_to(cluster)

    return m


# ══════════════════════════════════════════════════════════════════════════════
#  ARAYÜZ
# ══════════════════════════════════════════════════════════════════════════════

# ── Dil seçimi — sidebar render edilmeden önce çalışmalı ─────────────────────
# st.session_state'den önceki seçimi oku, yoksa TR varsayılan
_lang_default_idx = 0 if st.session_state.get("lang_choice", "TR") == "TR" else 1

# Sidebar dışında, ana akışın en başında dil belirle
with st.sidebar:
    # ── Dil Seçimi / Language Selection ───────────────────────────────────────
    lang_choice = st.radio("🌐 Dil / Language", ["TR", "EN"],
                           horizontal=True, index=_lang_default_idx,
                           key="lang_choice")
    L = LANG[lang_choice]
    st.markdown("---")

st.title(L["app_title"])
st.caption(L["app_caption"])

# ── Sidebar (devamı) ──────────────────────────────────────────────────────────
with st.sidebar:

    st.markdown(f"## {L['filters']}")
    st.markdown("---")

    tr_keys = list(RESOURCES.keys())
    if lang_choice == "EN":
        display_months = [tr_to_en_month(k) for k in tr_keys]
    else:
        display_months = tr_keys
    selected_month_display = st.selectbox(L["month"], display_months, index=0)
    # Her zaman TR key kullan (RESOURCES dict'i için)
    selected_month = selected_month_display if lang_choice == "TR" else en_to_tr_month(selected_month_display)

    hour_all = st.checkbox(L["all_hours"], value=True)
    selected_hour = None
    if not hour_all:
        selected_hour = st.slider(L["hour"], 0, 23, 8, format="%d:00")

    day_all = st.checkbox(L["all_days"], value=True)
    selected_day = None
    if not day_all:
        selected_day = st.slider(L["day"], 1, 31, 1)

    st.markdown("---")

    viz_opts = [L["viz_heat"], L["viz_circle"], L["viz_cluster"]]
    view_mode = st.radio(L["viz_mode"], viz_opts, index=0)

    st.markdown("---")

    limit = st.select_slider(
        L["record_limit"],
        options=[1000, 5000, 10000, 25000, 50000, 100000],
        value=10000,
    )

    st.markdown("---")
    st.markdown(L["color_legend"])

    st.markdown("---")
    st.markdown(f"## {L['ev_settings']}")
    cs_enabled = st.toggle(L.get("cs_enabled", "⚡ Charging Stations"), value=True)
    if cs_enabled:
        cs_aralik  = st.slider(L["cs_interval"], 0.2, 5.0, 1.0, 0.1)
        cs_guc     = st.selectbox(L["cs_power"], [22, 50, 100, 150, 200, 350], index=1)
        cs_verim   = st.slider(L["cs_efficiency"], 0.80, 0.99, 0.95, 0.01)
        cs_boy     = st.slider(L["cs_length"], 5, 1000, 10, 5)
        cs_delay   = st.slider(L["cs_delay"], 0, 10, 0, 1)
        cs_transit = st.checkbox(L["cs_transit"], value=True)
    else:
        cs_aralik = cs_guc = cs_verim = cs_boy = cs_delay = cs_transit = None

# ── Session state ─────────────────────────────────────────────────────────────
for key in ["df", "loaded_month", "loaded_hour", "loaded_day",
            "sumo_zip", "dogrulama_harita_html",
            "manual_points"]:
    if key not in st.session_state:
        st.session_state[key] = None if key != "manual_points" else []

df = st.session_state.df

# ── Ana içerik ────────────────────────────────────────────────────────────────
if df is not None and not df.empty:

    # İstatistik kartları
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric(L["cells"],     f"{len(df):,}")
    c2.metric(L["total_veh"], f"{int(df['NUMBER_OF_VEHICLES'].sum()):,}")
    c3.metric(L["avg_speed"], f"{df['AVERAGE_SPEED'].mean():.1f} km/h")
    c4.metric(L["max_veh"],   f"{int(df['NUMBER_OF_VEHICLES'].max()):,}")
    lh = st.session_state.loaded_hour
    ld = st.session_state.loaded_day
    c5.metric(L["hour_day"],
              f"{'%02d:00' % lh if lh is not None else L['readme_all']} / {ld if ld else L['readme_all']}")

    st.markdown("---")

    # Harita + yan panel
    map_col, info_col = st.columns([3, 1])

    with map_col:
        st.markdown(f"#### {L['map_title']} {st.session_state.loaded_month} — {view_mode}")
        with st.spinner("..."):
            m = build_map(df, view_mode, L)
        st_folium(m, width=None, height=520, returned_objects=[])

    with info_col:
        st.markdown(L["speed_dist"])
        hiz = df["AVERAGE_SPEED"].dropna()
        if not hiz.empty:
            hizli = int((hiz >= 60).sum())
            orta  = int(((hiz >= 30) & (hiz < 60)).sum())
            yavas = int((hiz < 30).sum())
            total = hizli + orta + yavas
            for lbl, val, emoji in [(L["fast"],   hizli, "🟢"),
                                     (L["medium"], orta,  "🟠"),
                                     (L["slow"],   yavas, "🔴")]:
                st.markdown(f"{emoji} **{lbl}:** {val} ({val/total*100:.1f}%)")
                st.progress(val / total)

        st.markdown("---")
        st.markdown(L["hourly"])
        if "_hour" in df.columns:
            hourly = df.groupby("_hour")["NUMBER_OF_VEHICLES"].sum().reset_index()
            hourly.columns = ["Hour", "Vehicles"]
            st.bar_chart(hourly.set_index(hourly.columns[0]), height=180)

    # Ham veri
    with st.expander(L["raw_data"]):
        cols = ["DATE_TIME", "LATITUDE", "LONGITUDE", "GEOHASH",
                "MINIMUM_SPEED", "AVERAGE_SPEED", "MAXIMUM_SPEED", "NUMBER_OF_VEHICLES"]
        st.dataframe(df[cols].head(500), use_container_width=True)
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(L["csv_dl"], csv,
                           f"trafik_{selected_month.replace(' ','_')}.csv", "text/csv")

    # ══════════════════════════════════════════════════════════════════════════
    #  SUMO EXPORT BÖLÜMÜ
    # ══════════════════════════════════════════════════════════════════════════
    st.markdown("---")
    st.markdown(L["sumo_title"])

    if not OSMNX_OK:
        st.warning(L["osmnx_warn"])
    else:
        col_sol, col_sag = st.columns([2, 1])

        with col_sol:
            st.markdown(L["export_settings"])

            # ── Bölge seçim modu ─────────────────────────────────────────────
            region_mode = st.radio(
                "📌",
                [L["region_select"], L["manual_select"]],
                horizontal=True,
                label_visibility="collapsed",
            )

            if region_mode == L["region_select"]:
                # ── Hazır bölge listesi ───────────────────────────────────────
                bolge_adi = st.selectbox(
                    L["region_select"],
                    list(BOLGE_TANIMLARI.keys()),
                    index=0,
                    help=L["region_help"],
                    label_visibility="collapsed",
                )
                bolge = BOLGE_TANIMLARI[bolge_adi]
                bbox  = bolge["bbox"]
                bolge_place = bolge["place"]

            else:
                # ── Haritadan elle seçim ──────────────────────────────────────
                bolge_adi = "CustomArea"
                bolge_place = None

                st.info(L["manual_hint"])

                padding = st.slider(L["manual_padding"], 0.002, 0.020, 0.005, 0.001,
                                    format="%.3f°")

                col_clr1, col_clr2 = st.columns([1, 1])
                with col_clr1:
                    if st.button(L["manual_clear"], use_container_width=True):
                        st.session_state.manual_points = []
                        st.session_state.sumo_zip = None

                pts = st.session_state.manual_points or []
                with col_clr2:
                    st.markdown(f"**{len(pts)} {L['manual_points']}**")

                # Seçim haritası
                st.markdown(L["manual_map_click"])
                sel_center = [41.01, 29.0]
                if pts:
                    sel_center = [sum(p[0] for p in pts)/len(pts),
                                  sum(p[1] for p in pts)/len(pts)]

                sel_map = folium.Map(location=sel_center, zoom_start=12,
                                     tiles="CartoDB dark_matter")

                # Mevcut noktaları çiz
                for idx, (plat, plon) in enumerate(pts):
                    folium.Marker(
                        [plat, plon],
                        icon=folium.DivIcon(
                            html=f'<div style="background:#f0a030;color:#000;border-radius:50%;'
                                 f'width:24px;height:24px;text-align:center;line-height:24px;'
                                 f'font-weight:bold;font-size:12px;">{idx+1}</div>',
                            icon_size=(24, 24), icon_anchor=(12, 12)
                        ),
                        tooltip=f"#{idx+1} ({plat:.4f}, {plon:.4f})"
                    ).add_to(sel_map)

                # Eğer yeterli nokta varsa bounding box çiz
                if len(pts) >= 3:
                    lats = [p[0] for p in pts]
                    lons = [p[1] for p in pts]
                    mn_lat = min(lats) - padding
                    mx_lat = max(lats) + padding
                    mn_lon = min(lons) - padding
                    mx_lon = max(lons) + padding
                    folium.Rectangle(
                        bounds=[[mn_lat, mn_lon], [mx_lat, mx_lon]],
                        color="#2ecc71", fill=True, fill_opacity=0.08,
                        weight=2, dash_array="6"
                    ).add_to(sel_map)

                map_result = st_folium(sel_map, width=None, height=380,
                                       returned_objects=["last_clicked"])

                # Tıklama → yeni nokta ekle
                if map_result and map_result.get("last_clicked"):
                    click = map_result["last_clicked"]
                    new_pt = (round(click["lat"], 6), round(click["lng"], 6))
                    if new_pt not in (st.session_state.manual_points or []):
                        if st.session_state.manual_points is None:
                            st.session_state.manual_points = []
                        if len(st.session_state.manual_points) < 8:
                            st.session_state.manual_points.append(new_pt)
                            st.rerun()

                pts = st.session_state.manual_points or []
                if len(pts) >= 3:
                    lats = [p[0] for p in pts]
                    lons = [p[1] for p in pts]
                    bbox = (min(lats)-padding, max(lats)+padding,
                            min(lons)-padding, max(lons)+padding)
                    st.success(f"{L['manual_bbox_ready']}: "
                               f"({bbox[0]:.4f},{bbox[2]:.4f}) → ({bbox[1]:.4f},{bbox[3]:.4f})")
                else:
                    st.warning(L["manual_need_more"])
                    bbox = None

            # Bölgedeki nokta sayısını önizle
            if bbox is not None:
                df_bolge = bbox_filtrele(df, bbox)
                st.info(f"📍 **{bolge_adi}** — **{len(df_bolge):,}** {L['points_found']}")
            else:
                df_bolge = pd.DataFrame()

            netconvert_yap = st.checkbox(
                L["netconvert_chk"],
                value=True,
                help=L["netconvert_help"],
            )

            # ── Fleet Mode ────────────────────────────────────────────────────
            st.markdown(f"---\n### {L['fleet_mode']}")

            if "fleet_mode" not in st.session_state:
                st.session_state.fleet_mode = "EV"

            fleet_col1, fleet_col2, fleet_col3 = st.columns(3)
            with fleet_col1:
                is_ev = st.session_state.fleet_mode == "EV"
                ev_btn = st.button(
                    ("✅ " if is_ev else "") + L["fleet_ev"],
                    use_container_width=True,
                    type="primary" if is_ev else "secondary",
                    key="fleet_btn_ev",
                )
            with fleet_col2:
                is_fuel = st.session_state.fleet_mode == "FUEL"
                fuel_btn = st.button(
                    ("✅ " if is_fuel else "") + L["fleet_fuel"],
                    use_container_width=True,
                    type="primary" if is_fuel else "secondary",
                    key="fleet_btn_fuel",
                )
            with fleet_col3:
                is_hyb = st.session_state.fleet_mode == "HYBRID"
                hyb_btn = st.button(
                    ("✅ " if is_hyb else "") + L["fleet_hybrid"],
                    use_container_width=True,
                    type="primary" if is_hyb else "secondary",
                    key="fleet_btn_hyb",
                )

            if ev_btn:
                st.session_state.fleet_mode = "EV"
                st.session_state.sumo_zip = None
                st.rerun()
            if fuel_btn:
                st.session_state.fleet_mode = "FUEL"
                st.session_state.sumo_zip = None
                st.rerun()
            if hyb_btn:
                st.session_state.fleet_mode = "HYBRID"
                st.session_state.sumo_zip = None
                st.rerun()

            fleet_mode = st.session_state.fleet_mode
            mode_emoji = {"EV": "⚡", "FUEL": "⛽", "HYBRID": "🔀"}
            mode_color = {"EV": ("#1a472a", "#2ecc71"), "FUEL": ("#4a1a1a", "#e74c3c"), "HYBRID": ("#1a2a4a", "#3498db")}
            bg, border = mode_color[fleet_mode]
            st.markdown(
                f"<div style='padding:8px 14px;border-radius:8px;background:{bg};"
                f"border:2px solid {border};display:inline-block;margin-top:4px;'>"
                f"<b>{mode_emoji[fleet_mode]} {fleet_mode}</b></div>",
                unsafe_allow_html=True
            )

            hybrid_ev_ratio = 0.40
            if fleet_mode == "HYBRID":
                hybrid_ev_ratio = st.slider(L["hybrid_ev_ratio"], 10, 90, 40, 5) / 100.0
                fuel_ratio = int((1 - hybrid_ev_ratio) * 100)
                ev_ratio   = int(hybrid_ev_ratio * 100)
                st.caption(f"⚡ EV {ev_ratio}%  +  ⛽ FUEL {fuel_ratio}%")

        with col_sag:
            st.markdown(L["output_files"])
            st.markdown("""
            ZIP:
            - `network.osm`
            - `network.net.xml`
            - `edgedata_ibb.xml`
            - `edgedata.add.xml`
            - `charging_stations.add.xml`
            - `routes.rou.xml`
            - `simulation.sumocfg`
            - `snap_report.csv`
            - `README.txt`
            """)

        if bbox is None or len(df_bolge) == 0:
            st.warning(L["no_data_warn"])
        else:
            export_btn = st.button(
                f"🚀 {bolge_adi} — {L['export_btn']}  [{fleet_mode}]",
                type="primary",
                use_container_width=False,
            )

            if export_btn:
                with st.spinner(L["fetching_osm"]):
                    try:
                        if bolge_place:
                            G = osm_ag_cek(bolge_place)
                        else:
                            mn_lat, mx_lat, mn_lon, mx_lon = bbox
                            G = ox.graph_from_bbox(
                                mx_lat, mn_lat, mx_lon, mn_lon,
                                network_type="drive"
                            )
                            G = ox.add_edge_speeds(G)
                            G = ox.add_edge_travel_times(G)
                        st.success(f"✅ OSM: {len(G.nodes):,} nodes, {len(G.edges):,} edges")
                    except Exception as e:
                        st.error(f"OSM error: {e}")
                        G = None

                if G is not None:
                    with st.spinner(L["snapping"]):
                        df_snap = nearest_edge_snap(G, df_bolge)
                        edge_ozet = edge_ozeti_hesapla(df_snap)
                        st.success(f"✅ {len(df_snap):,} points → {len(edge_ozet):,} edges")

                    with st.spinner(L["generating"]):
                        tmpdir = tempfile.mkdtemp()
                        osm_path = osm_xml_uret(G)

                        edgedata_xml = edgedata_xml_uret(
                            edge_ozet,
                            st.session_state.loaded_hour,
                            st.session_state.loaded_day
                        )

                        veh_xml_placeholder = vehicles_xml_uret(
                            edge_ozet, G, None,
                            st.session_state.loaded_hour,
                            fleet_mode=fleet_mode,
                            hybrid_ev_ratio=hybrid_ev_ratio,
                        )
                        veh_path = os.path.join(tmpdir, "routes.rou.xml")
                        with open(veh_path, "w") as f:
                            f.write(veh_xml_placeholder)

                        sumo_cfg_uret(tmpdir, st.session_state.loaded_hour,
                                      cs_enabled=(cs_enabled and fleet_mode in ("EV", "HYBRID")))
                        edgedata_additional_xml_uret(tmpdir)

                        snap_csv = df_snap[["LATITUDE", "LONGITUDE", "GEOHASH",
                                           "AVERAGE_SPEED", "NUMBER_OF_VEHICLES",
                                           "edge_u", "edge_v", "edge_key", "snap_dist"]].to_csv(index=False)

                        lh_str = f"{st.session_state.loaded_hour:02d}:00" if st.session_state.loaded_hour is not None else L["readme_all"]
                        readme = f"""{L['readme_title']}
================================
{L['readme_region']}: {bolge_adi}
{L['readme_month']}  : {st.session_state.loaded_month}
{L['readme_hour']}   : {lh_str}
{L['readme_fleet']}  : {fleet_mode}
Points  : {len(df_snap):,}
Edges   : {len(edge_ozet):,}

USAGE
-----
1. Extract ZIP to a folder.
2. Run: sumo-gui -c simulation.sumocfg
"""

                        # net.xml üret (netconvert varsa)
                        net_xml_ok = False
                        if netconvert_yap:
                            ok, net_result = sumo_net_xml_uret(osm_path, tmpdir)
                            if ok:
                                net_xml_ok = True
                                st.success("✅ netconvert → network.net.xml")
                            else:
                                st.warning(f"⚠️ netconvert failed: {net_result}")

                        # net.xml hazırsa gerçek edge ID'leriyle yeniden üret
                        net_path_tmp = os.path.join(tmpdir, "network.net.xml") if net_xml_ok else None
                        veh_xml_final = vehicles_xml_uret(
                            edge_ozet, G, net_path_tmp,
                            st.session_state.loaded_hour,
                            fleet_mode=fleet_mode,
                            hybrid_ev_ratio=hybrid_ev_ratio,
                        )
                        with open(veh_path, "w") as f:
                            f.write(veh_xml_final)

                        import re as _re
                        veh_count = len(_re.findall(r"<vehicle ", veh_xml_final))
                        ev_count   = len(_re.findall(r'type="evCar"',   veh_xml_final))
                        fuel_count = len(_re.findall(r'type="fuelCar"', veh_xml_final))
                        st.success(
                            f"✅ {veh_count:,} vehicles — "
                            f"⚡ EV: {ev_count:,}  ⛽ FUEL: {fuel_count:,}"
                        )
                        routes_path_final = veh_path

                        # Charging stations — placeholder only in FUEL-only mode
                        cs_xml = ""
                        if cs_enabled and net_xml_ok and fleet_mode in ("EV", "HYBRID"):
                            with st.spinner(L["generating_cs"]):
                                cs_xml = charging_stations_xml_uret(
                                    net_path_tmp,
                                    aralik_km    = cs_aralik,
                                    guc_kw       = float(cs_guc),
                                    verim        = cs_verim,
                                    transit_sarj = cs_transit,
                                    boy_m        = float(cs_boy),
                                    delay        = int(cs_delay),
                                )
                                import re as _re2
                                cs_count = len(_re2.findall(r"<chargingStation ", cs_xml))
                                st.success(f"✅ {cs_count:,} charging stations")

                        # ZIP paketle
                        dosyalar = {
                            "network.osm":                  osm_path,
                            "edgedata_ibb.xml":             edgedata_xml,
                            "edgedata.add.xml":             open(os.path.join(tmpdir, "edgedata.add.xml")).read(),
                            "simulation.sumocfg":           open(os.path.join(tmpdir, "simulation.sumocfg")).read(),
                            "snap_report.csv":              snap_csv,
                            "README.txt":                   readme,
                            "output/.gitkeep":              "",
                        }
                        if cs_enabled and cs_xml and fleet_mode in ("EV", "HYBRID"):
                            dosyalar["charging_stations.add.xml"] = cs_xml
                        if net_xml_ok:
                            dosyalar["network.net.xml"] = os.path.join(tmpdir, "network.net.xml")
                        dosyalar["routes.rou.xml"] = routes_path_final

                        zip_bytes = zip_olarak_paketle(dosyalar)
                        st.session_state.sumo_zip = zip_bytes

                        # Doğrulama haritası
                        with st.spinner("🗺️ Generating validation map…"):
                            hm = dogrulama_haritasi_olustur(df_bolge, df_snap, edge_ozet, G)
                            st.session_state.dogrulama_harita_html = hm._repr_html_()

            # Eğer ZIP hazırsa göster
            if st.session_state.sumo_zip:
                st.success(L["zip_ready"])

                dl_col, info_col2 = st.columns([1, 2])
                with dl_col:
                    st.download_button(
                        label=L["zip_dl"],
                        data=st.session_state.sumo_zip,
                        file_name=f"sumo_{bolge_adi}_{st.session_state.loaded_month.replace(' ','_')}_{fleet_mode}.zip",
                        mime="application/zip",
                        type="primary",
                        use_container_width=True,
                    )

                # Doğrulama haritası
                if st.session_state.dogrulama_harita_html:
                    with st.expander(L["validation_map"], expanded=True):
                        st.components.v1.html(
                            st.session_state.dogrulama_harita_html,
                            height=500,
                            scrolling=False
                        )

else:
    st.markdown(f"""
    <div style="text-align:center; padding: 80px 20px; color: #555;">
        <div style="font-size: 72px; margin-bottom: 20px;">🗺️</div>
        <h2 style="color: #f0a030 !important;">{L['start_hint']}</h2>
        <p style="font-size: 16px; max-width: 500px; margin: 0 auto; line-height: 1.7;">
            {L['start_hint2']}
        </p>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  FAZ 2 — SİMÜLASYON ANALİZİ (tripinfo.xml + emission.xml yükle & görselleştir)
# ══════════════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(L["analysis_title"])
st.markdown(L["analysis_desc"])

def parse_tripinfo(uploaded_file) -> pd.DataFrame:
    """
    tripinfo.xml → DataFrame.

    If battery device is active, each <tripinfo> has a <battery> sub-element:
      totalEnergyConsumed    → Wh (toplam harcanan)
      totalEnergyRegenerated → Wh (rejeneratif frenleme)
      actualBatteryCapacity  → Wh (son SoC)
      energyCharged          → Wh (energy received from charging station)

    Emissions device aktifse <emissions> alt elementi:
      fuel_abs → mg, CO2_abs → mg, NOx_abs → mg, PMx_abs → mg
    """
    tree = ET.parse(uploaded_file)
    rows = []
    for trip in tree.getroot().findall("tripinfo"):
        row = {
            "vehicle_id":     trip.get("id"),
            "depart":         float(trip.get("depart", 0)),
            "arrival":        float(trip.get("arrival", -1)),
            "duration_s":     float(trip.get("duration", 0)),
            "route_length_m": float(trip.get("routeLength", 0)),
            "wait_time_s":    float(trip.get("waitingTime", 0)),
            "time_loss_s":    float(trip.get("timeLoss", 0)),
            "depart_delay_s": float(trip.get("departDelay", 0)),
            "vtype":          trip.get("vType", "car"),
            # Battery (EV)
            "batt_consumed_wh": 0.0,
            "batt_regen_wh":    0.0,
            "batt_charged_wh":  0.0,
            "batt_soc_wh":      None,
            "batt_max_wh":      64000.0,
            "batt_depleted":    0,
            # Emission (FUEL)
            "fuel_abs_mg":   0.0,
            "co2_abs_mg":    0.0,
            "nox_abs_mg":    0.0,
            "pmx_abs_mg":    0.0,
            "elec_abs_wh":   0.0,
        }
        batt = trip.find("battery")
        if batt is not None:
            row["batt_consumed_wh"] = float(batt.get("totalEnergyConsumed",    0))
            row["batt_regen_wh"]    = float(batt.get("totalEnergyRegenerated", 0))
            row["batt_charged_wh"]  = float(batt.get("energyCharged",          0))
            row["batt_soc_wh"]      = float(batt.get("actualBatteryCapacity",  64000))
            row["batt_depleted"]    = int(batt.get("depleted", 0))
        emis = trip.find("emissions")
        if emis is not None:
            row["fuel_abs_mg"]   = float(emis.get("fuel_abs",        0))
            row["co2_abs_mg"]    = float(emis.get("CO2_abs",         0))
            row["nox_abs_mg"]    = float(emis.get("NOx_abs",         0))
            row["pmx_abs_mg"]    = float(emis.get("PMx_abs",         0))
            row["elec_abs_wh"]   = float(emis.get("electricity_abs", 0))  # Wh (EV/HYBRID)
        rows.append(row)

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["route_length_km"] = df["route_length_m"] / 1000
    df["avg_speed_kmh"]   = np.where(df["duration_s"] > 0,
                                     df["route_length_m"] / df["duration_s"] * 3.6, 0)
    df["arrived"] = df["arrival"] >= 0

    # Battery dönüşümleri (kWh)
    df["batt_consumed_kwh"] = df["batt_consumed_wh"] / 1000
    df["batt_regen_kwh"]    = df["batt_regen_wh"]    / 1000
    df["batt_charged_kwh"]  = df["batt_charged_wh"]  / 1000
    df["batt_net_kwh"]      = (df["batt_consumed_kwh"] - df["batt_regen_kwh"]
                                - df["batt_charged_kwh"])
    df["batt_soc_pct"]      = np.where(
        df["batt_soc_wh"].notna(),
        (df["batt_soc_wh"] / df["batt_max_wh"] * 100).clip(0, 100), 50.0)
    df["kwh_per_km"] = np.where(df["route_length_km"] > 0,
                                df["batt_consumed_kwh"] / df["route_length_km"], 0)

    # Yakıt & emisyon dönüşümleri
    # tripinfo <emissions> alanları kümülatif trip toplamı — süreyle çarpmaya GEREK YOK
    FUEL_DENSITY = 820_000.0   # mg/L (benzin: 0.820 g/mL)
    df["fuel_g"]      = df["fuel_abs_mg"]  / 1_000         # mg → g
    df["co2_g"]       = df["co2_abs_mg"]   / 1_000         # mg → g
    df["nox_mg"]      = df["nox_abs_mg"]                   # zaten mg
    df["pmx_mg"]      = df["pmx_abs_mg"]                   # zaten mg
    df["fuel_L"]      = df["fuel_abs_mg"]  / FUEL_DENSITY  # mg → L
    df["co2_kg"]      = df["co2_abs_mg"]   / 1_000_000     # mg → kg
    df["elec_abs_kwh"]= df["elec_abs_wh"]  / 1_000         # Wh → kWh (EV/HYBRID egzoz elektrik)
    df["lper100km"]   = np.where(df["route_length_km"] > 0,
                                 df["fuel_L"] / df["route_length_km"] * 100, 0)
    df["co2_per_km"]  = np.where(df["route_length_km"] > 0,
                                 df["co2_g"]  / df["route_length_km"], 0)  # g/km
    return df



def parse_cs_output(cs_file) -> tuple:
    """
    Parse SUMO chargingstations-output XML.

    SUMO format (chargingstations-output.xml):
    <chargingStations>
      <chargingStation id="cs_edge_0"
                       totalEnergyCharged="12345.6"   <!-- Wh -->
                       chargingEvents="42">
        <vehicle id="veh_1"
                 totalEnergyChargedIntoVehicle="234.5"  <!-- Wh -->
                 chargingBegin="100.0"
                 chargingEnd="200.0"
                 partialCharge="234.5"/>
        ...
      </chargingStation>
      ...
    </chargingStations>

    Returns
    -------
    df_stations : per-station summary DataFrame
    df_events   : per-event (vehicle × station) DataFrame
    df_veh      : per-vehicle aggregated charging DataFrame
    """
    import xml.etree.ElementTree as ET
    import io, pandas as pd

    if cs_file is None:
        empty = pd.DataFrame()
        return empty, empty, empty

    try:
        raw = cs_file.read()
        if hasattr(cs_file, "seek"):
            cs_file.seek(0)
        tree = ET.fromstring(raw)
    except Exception as e:
        st.error(f"chargingstations_output.xml parse error: {e}")
        empty = pd.DataFrame()
        return empty, empty, empty

    station_rows = []
    event_rows   = []

    for cs in tree.iter("chargingStation"):
        cs_id     = cs.get("id", "")
        total_wh  = float(cs.get("totalEnergyCharged", 0))
        n_events  = int(cs.get("chargingEvents", 0))

        station_rows.append({
            "station_id":          cs_id,
            "total_charged_kwh":   total_wh / 1000.0,
            "charging_events":     n_events,
        })

        for veh in cs.findall("vehicle"):
            event_rows.append({
                "station_id":      cs_id,
                "vehicle_id":      veh.get("id", ""),
                "charged_kwh":     float(veh.get("totalEnergyChargedIntoVehicle", 0)) / 1000.0,
                "charge_begin_s":  float(veh.get("chargingBegin", 0)),
                "charge_end_s":    float(veh.get("chargingEnd",   0)),
                "partial_kwh":     float(veh.get("partialCharge", 0)) / 1000.0,
            })

    df_stations = pd.DataFrame(station_rows) if station_rows else pd.DataFrame(
        columns=["station_id","total_charged_kwh","charging_events"])
    df_events   = pd.DataFrame(event_rows) if event_rows else pd.DataFrame(
        columns=["station_id","vehicle_id","charged_kwh","charge_begin_s","charge_end_s","partial_kwh"])

    # Per-vehicle aggregate
    if not df_events.empty:
        df_veh = (df_events.groupby("vehicle_id")
                  .agg(
                      total_charged_kwh = ("charged_kwh",    "sum"),
                      n_stations_used   = ("station_id",     "nunique"),
                      n_charge_events   = ("charged_kwh",    "count"),
                      first_charge_s    = ("charge_begin_s", "min"),
                      last_charge_s     = ("charge_end_s",   "max"),
                  )
                  .reset_index())
    else:
        df_veh = pd.DataFrame(
            columns=["vehicle_id","total_charged_kwh","n_stations_used",
                     "n_charge_events","first_charge_s","last_charge_s"])

    return df_stations, df_events, df_veh

def merge_outputs(trip_f, batt_f=None):
    """
    Sadece tripinfo.xml parse eder.
    Fuel, emissions (fuel_abs, CO2_abs, NOx_abs, PMx_abs, electricity_abs)
    and battery data come as cumulative totals from tripinfo — no emission.xml needed.
    """
    df_t = parse_tripinfo(trip_f) if trip_f else pd.DataFrame()
    df_e = pd.DataFrame()   # kept empty for backward compatibility

    df = df_t.copy() if not df_t.empty else pd.DataFrame()

    if not df.empty and "route_length_km" in df.columns:
        if "fuel_L" in df.columns:
            df["fuel_per_km"] = np.where(df["route_length_km"] > 0,
                                         df["fuel_L"] / df["route_length_km"], np.nan)

    # df_batt uyumlu görünüm — fleet_panel için tripinfo battery sütunlarından
    df_b = pd.DataFrame()
    if not df_t.empty and "batt_consumed_kwh" in df_t.columns:
        ev_mask = df_t["vtype"] == "evCar" if "vtype" in df_t.columns else pd.Series(True, index=df_t.index)
        df_b = df_t[ev_mask][["vehicle_id",
                               "batt_consumed_kwh", "batt_regen_kwh",
                               "batt_charged_kwh",  "batt_net_kwh",
                               "batt_soc_pct",      "batt_depleted"]].copy()
        df_b.rename(columns={
            "batt_consumed_kwh": "energy_consumed_kwh",
            "batt_regen_kwh":    "energy_regen_kwh",
            "batt_charged_kwh":  "energy_charged_kwh",
            "batt_net_kwh":      "net_consumption_kwh",
            "batt_soc_pct":      "final_soc_pct",
            "batt_depleted":     "charging_events",
        }, inplace=True)
        df_b = df_b[df_b["energy_consumed_kwh"] > 0]  # zero consumption = not EV

    return df, df_t, df_e, df_b


def fleet_panel(df, df_trip, df_emis, df_batt, label, fiyat_yakit, fiyat_elec, curr_sym="₺", conv=1.0):
    """Summary metrics + charts + cost for a single fleet."""
    if df.empty:
        st.info(L["no_files"])
        return

    # ── Simülasyon Özeti ────────────────────────────────────────────────────
    st.markdown(L["fleet_summary"])
    k1, k2, k3, k4, k5, k6 = st.columns(6)
    if not df_trip.empty:
        k1.metric(L["met_total_veh"],  f"{len(df_trip):,}")
        k2.metric(L["met_arrived"],    f"{df_trip['arrived'].sum():,}")
        k3.metric(L["met_avg_route"],  f"{df_trip['route_length_km'].mean():.2f} km")
        k4.metric(L["met_avg_dur"],    f"{df_trip['duration_s'].mean():.0f} s")
        k5.metric(L["met_avg_spd"],    f"{df_trip['avg_speed_kmh'].mean():.1f} km/h")
        k6.metric(L["met_avg_wait"],   f"{df_trip['wait_time_s'].mean():.0f} s")

    # ── Yakıt/Emisyon veya EV metrikleri ────────────────────────────────────
    # ── Emisyon: tripinfo (fuel_abs_mg) doğru kaynak, emission.xml period=30 nedeniyle eksik
    # tripinfo her araç için trip sonu kümülatif toplam verir (mg cinsinden)
    # emission.xml period=30+step-scaled=1s → gerçek verinin ~1/30'u kaydedilir
    _FUEL_DENSITY_MG = 820_000  # mg/L (benzin: 0.820 kg/L)
    has_fuel = (not df_trip.empty and "fuel_abs_mg" in df_trip.columns
                and df_trip["fuel_abs_mg"].sum() > 0)

    # tripinfo'dan kümülatif toplamlar (mg)
    t_fuel_mg  = df_trip["fuel_abs_mg"].sum()  if (not df_trip.empty and "fuel_abs_mg" in df_trip.columns) else 0.0
    t_co2_mg   = df_trip["co2_abs_mg"].sum()   if (not df_trip.empty and "co2_abs_mg"  in df_trip.columns) else 0.0
    t_nox_mg   = df_trip["nox_abs_mg"].sum()   if (not df_trip.empty and "nox_abs_mg"  in df_trip.columns) else 0.0
    t_pmx_mg   = df_trip["pmx_abs_mg"].sum()   if (not df_trip.empty and "pmx_abs_mg"  in df_trip.columns) else 0.0
    # Gürültü: emission.xml'den (tripinfo'da yok) — ortalama dB mantıklı
    noise_avg  = df_emis["noise_avg_db"].mean() if (not df_emis.empty and "noise_avg_db" in df_emis.columns) else 0.0

    t_fuel_l   = t_fuel_mg / _FUEL_DENSITY_MG
    t_fuel_g   = t_fuel_mg / 1_000
    t_co2_kg   = t_co2_mg  / 1_000_000
    t_nox_mg_v = t_nox_mg
    t_pmx_mg_v = t_pmx_mg

    if has_fuel or not df_trip.empty:
        st.markdown(L["fuel_emis_summary"])
        e1, e2, e3, e4, e5, e6 = st.columns(6)
        if has_fuel:
            e1.metric(L["met_total_fuel_l"],  f"{t_fuel_l:.4f} L")
            e2.metric(L["met_total_fuel_g"],  f"{t_fuel_g:.2f} g")
            e3.metric(L["met_total_co2"],     f"{t_co2_kg:.4f} kg")
            e4.metric(L["met_total_nox"],     f"{t_nox_mg_v:.2f} mg")
            e5.metric(L["met_total_pm"],      f"{t_pmx_mg_v:.4f} mg")
            e6.metric(L["met_avg_noise"],     f"{noise_avg:.1f} dB" if noise_avg > 0 else "N/A")
        else:
            # EV: egzoz emisyonu yok
            e1.metric("🌿 Egzoz CO₂",    "0 kg")
            e2.metric("⛽ Fuel",          "0 L")
            e3.metric("🔴 NOx",           "0 mg")
            e4.metric("🔴 PMx",           "0 mg")
            e5.metric(L["met_avg_noise"], f"{noise_avg:.1f} dB" if noise_avg > 0 else "N/A")
            e6.metric("⚡ Type",          "EV — zero exhaust")

    if not df_batt.empty:
        st.markdown(L["ev_battery"])
        b1, b2, b3, b4, b5, b6 = st.columns(6)
        b1.metric(L["met_total_cons"],   f"{df_batt['energy_consumed_kwh'].sum():.3f} kWh")
        b2.metric(L.get("met_regen","♻️ Rejeneratif"), f"{df_batt['energy_regen_kwh'].sum():.3f} kWh")
        b3.metric(L["met_net_cons"],     f"{df_batt['net_consumption_kwh'].sum():.3f} kWh")
        b4.metric(L["met_total_charge"], f"{df_batt['energy_charged_kwh'].sum():.3f} kWh")
        b5.metric(L["met_avg_soc"],      f"{df_batt['final_soc_pct'].mean():.1f}%")
        b6.metric(L["met_perveh_kwh"],   f"{df_batt['energy_consumed_kwh'].mean():.3f} kWh")

    # ── Maliyet ──────────────────────────────────────────────────────────────
    st.markdown(L["cost_summary"])
    # tripinfo'dan gelen doğru yakıt değeri (emission.xml period=30 nedeniyle hatalı)
    total_fuel_l = t_fuel_l  # cumulative total from tripinfo
    # Net kWh = brüt tüketim - rejeneratif frenleme geri kazanımı
    # Şebekeden gerçekten alınan enerji bu kadardır → maliyet buna göre
    if not df_batt.empty and "net_consumption_kwh" in df_batt.columns:
        total_kwh_net = max(0.0, df_batt["net_consumption_kwh"].sum())
    else:
        total_kwh_net = df_batt["energy_consumed_kwh"].sum() if not df_batt.empty else 0.0
    total_kwh_gross = df_batt["energy_consumed_kwh"].sum() if not df_batt.empty else 0.0
    n_veh        = max(len(df_trip) if not df_trip.empty else len(df), 1)
    total_km     = df["route_length_km"].sum() if "route_length_km" in df.columns else 0.0

    cost_fuel = total_fuel_l * fiyat_yakit
    cost_elec = total_kwh_net * fiyat_elec   # net kWh ile maliyet
    total_cost = cost_fuel + cost_elec

    c1, c2, c3, c4 = st.columns(4)
    if cost_fuel > 0:
        c1.metric(L["met_fuel_cost"],     f"{curr_sym}{cost_fuel*conv:,.2f}")
    if cost_elec > 0:
        c2.metric(L["met_elec_cost"],     f"{curr_sym}{cost_elec*conv:,.2f}")
    c3.metric(L["met_cost_perveh"],       f"{curr_sym}{total_cost/n_veh*conv:,.2f}")
    if total_km > 0:
        c4.metric(L["met_cost_per100km"], f"{curr_sym}{total_cost/total_km*100*conv:,.2f}")

    # ── Dağılım Grafikleri ───────────────────────────────────────────────────
    st.markdown(L["dist_charts"])
    g1, g2 = st.columns(2)
    if not df_trip.empty:
        with g1:
            st.markdown(L["chart_route"])
            hist = df_trip["route_length_km"].clip(upper=df_trip["route_length_km"].quantile(0.99))
            bins = np.linspace(hist.min(), hist.max(), 30)
            c, e = np.histogram(hist, bins=bins)
            st.bar_chart(pd.DataFrame({L["col_route"]: (e[:-1]+e[1:])/2, L["col_vehicles"]: c}).set_index(L["col_route"]), height=220)
        with g2:
            st.markdown(L["chart_speed"])
            spd = df_trip["avg_speed_kmh"].clip(upper=df_trip["avg_speed_kmh"].quantile(0.99))
            bins2 = np.linspace(spd.min(), spd.max(), 30)
            c2_, e2 = np.histogram(spd, bins=bins2)
            st.bar_chart(pd.DataFrame({L["col_speed"]: (e2[:-1]+e2[1:])/2, L["col_vehicles"]: c2_}).set_index(L["col_speed"]), height=220)

    # Yakıt & CO2 histogramı — tripinfo tabanlı (doğru kümülatif değerler)
    _has_fuel_hist = not df.empty and "fuel_g" in df.columns and df["fuel_g"].sum() > 0
    if _has_fuel_hist:
        g3, g4 = st.columns(2)
        with g3:
            st.markdown(L["chart_fuel"])
            fuel = df["fuel_g"].clip(upper=df["fuel_g"].quantile(0.99))
            if fuel.max() > fuel.min():
                bins3 = np.linspace(fuel.min(), fuel.max(), 30)
                c3_, e3 = np.histogram(fuel, bins=bins3)
                st.bar_chart(pd.DataFrame({L["col_fuel_g"]: (e3[:-1]+e3[1:])/2, L["col_vehicles"]: c3_}).set_index(L["col_fuel_g"]), height=220)
        with g4:
            st.markdown(L["chart_co2"])
            co2 = df["co2_g"].clip(upper=df["co2_g"].quantile(0.99))
            if co2.max() > co2.min():
                bins4 = np.linspace(co2.min(), co2.max(), 30)
                c4_, e4 = np.histogram(co2, bins=bins4)
                st.bar_chart(pd.DataFrame({L["col_co2_g"]: (e4[:-1]+e4[1:])/2, L["col_vehicles"]: c4_}).set_index(L["col_co2_g"]), height=220)

    if not df_batt.empty:
        gb1, gb2 = st.columns(2)
        with gb1:
            st.markdown(L["chart_soc"])
            soc = df_batt["final_soc_pct"].clip(0, 100)
            bs = np.linspace(0, 100, 21)
            cs_, es = np.histogram(soc, bins=bs)
            st.bar_chart(pd.DataFrame({"SoC (%)": (es[:-1]+es[1:])/2, L["col_veh"]: cs_}).set_index("SoC (%)"), height=220)
        with gb2:
            st.markdown(L["chart_ec"])
            ec = df_batt["energy_consumed_kwh"].clip(upper=df_batt["energy_consumed_kwh"].quantile(0.99))
            if ec.max() > ec.min():
                be = np.linspace(ec.min(), ec.max(), 30)
                ce_, ee = np.histogram(ec, bins=be)
                st.bar_chart(pd.DataFrame({"kWh": (ee[:-1]+ee[1:])/2, L["col_veh"]: ce_}).set_index("kWh"), height=220)

    # ── Araç Bazlı Tablo ─────────────────────────────────────────────────────
    st.markdown(L["veh_detail"])
    display_cols, rename_map = [], {}
    col_map = [
        ("vehicle_id",           L["col_vid"]),
        ("route_length_km",      L["col_route"]),
        ("duration_s",           L["col_dur"]),
        ("avg_speed_kmh",        L["col_avgspd"]),
        ("wait_time_s",          L["col_wait"]),
        ("fuel_g",               L["col_fuel_g"]),
        ("fuel_L",               L["col_fuel_l"]),
        ("co2_g",                L["col_co2_g"]),
        ("nox_mg",               L["col_nox_mg"]),
        ("pmx_mg",               L["col_pm_mg"]),
        ("noise_avg_db",         L["col_noise_db"]),
        ("fuel_per_km",          "L/km"),
        ("co2_per_km",           L["col_co2_km"]),
        ("energy_consumed_kwh",  L["col_elec_kwh"]),
        ("energy_regen_kwh",     L.get("col_regen_kwh", "♻️ Rejeneratif (kWh)")),
        ("energy_charged_kwh",   L.get("col_charged_kwh", "🔌 Charged (kWh)")),
        ("net_consumption_kwh",  L["col_net_kwh"]),
        ("kwh_per_km",           L["col_kwh_km"]),
        ("final_soc_pct",        L["col_soc"]),
        ("charging_events",      L["col_charge_ev"]),
    ]
    for raw, nice in col_map:
        if raw in df.columns:
            display_cols.append(raw)
            rename_map[raw] = nice
    if display_cols:
        tbl = df[display_cols].rename(columns=rename_map)
        for col in tbl.select_dtypes(include=[float]).columns:
            tbl[col] = tbl[col].round(4)
        st.dataframe(tbl, use_container_width=True, height=300)
        ay_str = st.session_state.get("loaded_month", "sim") or "sim"
        st.download_button(
            L["btn_veh_csv"],
            tbl.to_csv(index=False).encode("utf-8"),
            f"vehicle_report_{label}_{ay_str.replace(' ','_')}.csv",
            "text/csv",
            key=f"dl_{label}"
        )

    # ── Dakikalık Profil ──────────────────────────────────────────────────────
    if not df_emis.empty and not df_trip.empty and "depart" in df.columns:
        st.markdown(L["hourly_profile"])
        df["depart_min"] = (df["depart"] % 3600) // 60
        min_grp = df.groupby("depart_min").agg(
            Fuel_g=("fuel_g", "sum"), CO2_g=("co2_g", "sum")
        ).reset_index().rename(columns={"depart_min": L["col_minute"]})
        cf, cc = st.columns(2)
        with cf:
            st.markdown(L["chart_fuel_min"])
            st.line_chart(min_grp.set_index(L["col_minute"])[["Fuel_g"]], height=180)
        with cc:
            st.markdown(L["chart_co2_min"])
            st.line_chart(min_grp.set_index(L["col_minute"])[["CO2_g"]], height=180)


def comparison_panel(fleets: dict, fiyat_yakit: float, fiyat_elec: float, curr_sym: str = "₺", conv: float = 1.0):
    """
    fleets = {
      "EV":     (df, df_trip, df_emis, df_batt),
      "FUEL":   (df, df_trip, df_emis, df_batt),
      "HYBRID": (df, df_trip, df_emis, df_batt),
    }
    """
    available = {k: v for k, v in fleets.items() if not v[0].empty}
    if len(available) < 2:
        st.info(L["compare_desc"])
        return

    st.markdown(L["compare_title"])

    rows = []
    for label, (df, df_t, df_e, df_b) in available.items():
        n_veh      = max(len(df_t) if not df_t.empty else len(df), 1)
        total_km   = df["route_length_km"].sum() if "route_length_km" in df.columns else 0
        # Net kWh: şebekeden alınan gerçek enerji (brüt - rejeneratif)
        if not df_b.empty and "net_consumption_kwh" in df_b.columns:
            total_kwh = max(0.0, df_b["net_consumption_kwh"].sum())
        else:
            total_kwh = df_b["energy_consumed_kwh"].sum() if not df_b.empty else 0
        # tripinfo'dan kümülatif doğru yakıt/CO2 (emission.xml period=30 nedeniyle hatalı)
        _FD_MG = 820_000
        total_fuel = (df_t["fuel_abs_mg"].sum() / _FD_MG
                      if (not df_t.empty and "fuel_abs_mg" in df_t.columns) else 0)
        # Egzoz CO₂: tripinfo co2_abs_mg (mg) → kg
        co2_exhaust = (df_t["co2_abs_mg"].sum() / 1_000_000
                       if (not df_t.empty and "co2_abs_mg" in df_t.columns) else 0)
        # Şebeke CO₂ (EV/HYBRID → Türkiye grid faktörü 0.45 kg/kWh)
        co2_grid    = total_kwh * 0.45
        total_co2_effective = co2_exhaust + co2_grid

        cost_fuel  = total_fuel * fiyat_yakit
        cost_elec  = total_kwh  * fiyat_elec
        total_cost = cost_fuel + cost_elec

        co2_per_veh  = total_co2_effective / n_veh if n_veh > 0 else 0
        co2_per_km   = total_co2_effective / total_km * 1000 if total_km > 0 else 0  # g/km
        kwh_per_km   = total_kwh / total_km * 100 if total_km > 0 else 0  # kWh/100km
        fuel_per_100 = total_fuel / total_km * 100 if total_km > 0 else 0  # L/100km
        cost_per_km  = total_cost / total_km * 100 if total_km > 0 else 0  # ₺/100km

        rows.append({
            L["col_fleet"]:        label,
            "n_veh":               n_veh,
            "total_km":            total_km,
            L["col_kwh_total"]:    round(total_kwh, 3),
            L["col_fuel_total_l"]: round(total_fuel, 4),
            "co2_exhaust_kg":      round(co2_exhaust, 4),
            "co2_grid_kg":         round(co2_grid, 4),
            L["col_co2_total"]:    round(total_co2_effective, 4),
            "CO₂/vehicle (g)":     round(co2_per_veh * 1000, 2),
            "CO₂/100km (g)":       round(co2_per_km,  2),
            "kWh/100km":           round(kwh_per_km,  3),
            "L/100km":             round(fuel_per_100, 3),
            L["col_total_cost"]:   round(total_cost * conv, 2),
            L["col_cost_perveh"]:  round(total_cost / n_veh * conv, 2),
            f"{curr_sym}/100km":             round(cost_per_km, 2),
        })

    df_cmp = pd.DataFrame(rows).set_index(L["col_fleet"])

    # ── Araç sayısı farkı uyarısı ────────────────────────────────────────────
    veh_counts = {k: v["n_veh"] for k, v in zip(df_cmp.index, rows)}
    max_veh = max(veh_counts.values())
    min_veh = min(veh_counts.values())
    if max_veh > min_veh * 1.2:
        veh_info = "  |  ".join(f"{k}: {v:,} vehicles" for k, v in veh_counts.items())
        st.warning(
            f"⚠️ **Fleets have different vehicle counts** — Use "
            "**per-100km normalized values** for comparison.  \n" + veh_info
        )

    # ── Grafik seçim radio ───────────────────────────────────────────────────
    chart_mode = st.radio(
        "📊 Chart mode",
        ["Total", "Per 100km (normalized)"],
        horizontal=True, index=1,   # default: normalize
        key="cmp_chart_mode"
    )
    norm = chart_mode == "Per 100km (normalized)"

    c1, c2 = st.columns(2)
    with c1:
        if norm:
            st.markdown(L["compare_energy"] + " *(kWh/100km)*")
            st.bar_chart(df_cmp[["kWh/100km"]], height=250)
        else:
            st.markdown(L["compare_energy"])
            energy_df = pd.DataFrame({
                "kWh (net)":      df_cmp[L["col_kwh_total"]],
                "Fuel (L→kWh)":   df_cmp[L["col_fuel_total_l"]] * 9.96,
            })
            st.bar_chart(energy_df, height=250)

    with c2:
        if norm:
            st.markdown(L["compare_emission"] + " *(g/100km)*")
            # CO2 g/100km yığılı: egzoz + şebeke oranlaması
            co2_norm_ex = (df_cmp["co2_exhaust_kg"] / df_cmp["total_km"].replace(0, float("nan")) * 100_000)
            co2_norm_gr = (df_cmp["co2_grid_kg"]    / df_cmp["total_km"].replace(0, float("nan")) * 100_000)
            co2_df = pd.DataFrame({
                "🚗 Egzoz (g/100km)":  co2_norm_ex.fillna(0),
                "⚡ Grid (g/100km)": co2_norm_gr.fillna(0),
            })
            st.bar_chart(co2_df, height=250)
        else:
            st.markdown(L["compare_emission"])
            co2_df = df_cmp[["co2_exhaust_kg", "co2_grid_kg"]].rename(columns={
                "co2_exhaust_kg": "🚗 Egzoz CO₂ (kg)",
                "co2_grid_kg":    "⚡ Grid CO₂ (kg)",
            })
            st.bar_chart(co2_df, height=250)

    c3, c4 = st.columns(2)
    with c3:
        if norm:
            st.markdown(L["compare_cost"] + " *(per 100km)*")
            st.bar_chart(df_cmp[[f"{curr_sym}/100km"]], height=250)
        else:
            st.markdown(L["compare_cost"])
            st.bar_chart(df_cmp[[L["col_total_cost"]]], height=250)
    with c4:
        st.markdown(L["compare_perveh"])
        st.bar_chart(df_cmp[[L["col_cost_perveh"]]], height=250)

    # ── Özet tablo ───────────────────────────────────────────────────────────
    # Tabloda hem toplam hem normalize sütunlar göster
    display_cols = [
        L["col_kwh_total"], "kWh/100km",
        L["col_fuel_total_l"], "L/100km",
        L["col_co2_total"], "CO₂/vehicle (g)", "CO₂/100km (g)",
        L["col_total_cost"], L["col_cost_perveh"], f"{curr_sym}/100km",
    ]
    display_df = df_cmp[[c for c in display_cols if c in df_cmp.columns]]
    norm_cols = [c for c in ["CO₂/100km (g)", f"{curr_sym}/100km", L["col_cost_perveh"]] if c in display_df.columns]
    st.dataframe(display_df.style.highlight_min(
        subset=norm_cols, color="#1a4a1a"
    ).highlight_max(
        subset=norm_cols, color="#4a1a1a"
    ), use_container_width=True)

    # ── EV vs FUEL tasarruf özeti ────────────────────────────────────────────
    if "EV" in available and "FUEL" in available:
        ev_row   = df_cmp.loc["EV"]
        fuel_row = df_cmp.loc["FUEL"]
        # Per-km bazlı karşılaştırma (filo büyüklüğünden bağımsız)
        cost_save_100km = fuel_row[f"{curr_sym}/100km"]     - ev_row[f"{curr_sym}/100km"]
        co2_save_100km  = fuel_row["CO₂/100km (g)"] - ev_row["CO₂/100km (g)"]
        cost_save_veh   = fuel_row[L["col_cost_perveh"]] - ev_row[L["col_cost_perveh"]]  # already in display currency
        pct_cost = cost_save_100km / max(fuel_row[f"{curr_sym}/100km"], 0.001) * 100
        pct_co2  = co2_save_100km  / max(fuel_row["CO₂/100km (g)"], 0.001) * 100
        st.markdown("---")
        st.caption("ℹ️ Savings metrics below are **normalized per 100 km** — fleet-size independent comparison.")
        s1, s2, s3 = st.columns(3)
        s1.metric(L["saving_vs_fuel"] + f" ({curr_sym}/100km)",      f"{curr_sym}{cost_save_100km*conv:,.2f}", f"{pct_cost:.1f}%", delta_color="normal")
        s2.metric(L["saving_vs_fuel"] + " (CO₂ g/100km)",  f"{co2_save_100km:.1f} g",  f"{pct_co2:.1f}%",  delta_color="normal")
        s3.metric(L["saving_vs_fuel"] + " /vehicle",
                  f"₺{cost_save_veh:.2f}", delta_color="normal")

    st.download_button(
        "⬇️ CSV",
        display_df.reset_index().to_csv(index=False).encode("utf-8"),
        "fleet_comparison.csv", "text/csv", key="dl_cmp"
    )


# ── Maliyet parametreleri + Veri Yükleme butonu (sidebar altında) ─────────────
# Döviz kuru sabitleri (güncellenmesi için sidebar'da gösterilir)
CURRENCY_RATES = {
    "TRY": {"symbol": "₺", "fuel_to_try": 1.0,   "elec_to_try": 1.0,   "label": "TRY (₺)"},
    "USD": {"symbol": "$", "fuel_to_try": 0.0,   "elec_to_try": 0.0,   "label": "USD ($)"},
    "EUR": {"symbol": "€", "fuel_to_try": 0.0,   "elec_to_try": 0.0,   "label": "EUR (€)"},
}
# Varsayılan dönüşüm oranları (kullanıcı sidebar'dan güncelleyebilir)
_DEFAULT_USD_RATE = 38.5   # 1 USD = 38.5 TRY (example default)
_DEFAULT_EUR_RATE = 41.5   # 1 EUR = 41.5 TRY (example default)

with st.sidebar:
    st.markdown("---")
    st.markdown(f"**{L['cost_settings']}**")
    st.caption(f"[{L['shell_link']}](https://www.shell.com.tr/suruculer/shell-yakitlari/akaryakit-pompa-satis-fiyatlari.html) | [{L['zes_link']}](https://zes.net/tr/fiyatlandirma)")

    # ── Para birimi seçici ───────────────────────────────────────────────
    currency = st.selectbox(
        L.get("currency_label", "💱 Currency"),
        ["TRY (₺)", "USD ($)", "EUR (€)"],
        index=0, key="currency_sel"
    )
    curr_code = currency[:3]  # "TRY", "USD", "EUR"

    # Kur girişi (TRY dışı için)
    if curr_code == "USD":
        usd_rate = st.number_input("1 USD = ? TRY", min_value=1.0, value=_DEFAULT_USD_RATE,
                                    step=0.5, format="%.2f", key="usd_rate")
        CURRENCY_RATES["USD"]["fuel_to_try"]  = usd_rate
        CURRENCY_RATES["USD"]["elec_to_try"]  = usd_rate
        curr_sym = "$"
        conv = 1.0 / usd_rate   # TRY → USD
    elif curr_code == "EUR":
        eur_rate = st.number_input("1 EUR = ? TRY", min_value=1.0, value=_DEFAULT_EUR_RATE,
                                    step=0.5, format="%.2f", key="eur_rate")
        CURRENCY_RATES["EUR"]["fuel_to_try"]  = eur_rate
        CURRENCY_RATES["EUR"]["elec_to_try"]  = eur_rate
        curr_sym = "€"
        conv = 1.0 / eur_rate   # TRY → EUR
    else:
        curr_sym = "₺"
        conv = 1.0              # TRY → TRY (no conversion)

    # ── Yakıt / elektrik fiyatları (seçilen para biriminde girilir) ──────
    fuel_label = L["fuel_price"].replace("₺", curr_sym).replace("TRY", curr_code)
    elec_label = L["elec_price"].replace("₺", curr_sym).replace("TRY", curr_code)

    # Varsayılan değerleri para birimine göre dönüştür
    default_fuel_try = 57.12
    default_elec_try = 16.49
    default_fuel_disp = round(default_fuel_try * conv, 3)
    default_elec_disp = round(default_elec_try * conv, 3)

    fiyat_yakit_disp = st.number_input(fuel_label, min_value=0.0,
                                        value=default_fuel_disp, step=0.01,
                                        help=L["fuel_price_help"], format="%.3f")
    fiyat_elec_disp  = st.number_input(elec_label, min_value=0.0,
                                        value=default_elec_disp, step=0.001,
                                        help=L["elec_price_help"], format="%.3f")

    # İç hesaplama her zaman TRY cinsinden → gösterim için conv kullanılır
    fiyat_yakit = fiyat_yakit_disp / conv   # convert entered value → TRY for calculations
    fiyat_elec  = fiyat_elec_disp  / conv   # convert entered value → TRY for calculations

    st.markdown("---")
    load_btn = st.button(L["load_btn"], type="primary", use_container_width=True)

# ── Veri yükleme (buton cost settings altında tanımlandığı için buraya taşındı) ──
if load_btn:
    resource_id = RESOURCES[selected_month]
    try:
        df_loaded = fetch_data(resource_id, selected_hour, selected_day, limit)
        st.session_state.df           = df_loaded
        st.session_state.loaded_month = selected_month
        st.session_state.loaded_hour  = selected_hour
        st.session_state.loaded_day   = selected_day
        st.session_state.sumo_zip     = None
        st.session_state.dogrulama_harita_html = None
        if df_loaded.empty:
            st.warning("⚠️ No records found. Try different filters.")
        else:
            st.success(f"✅ {len(df_loaded):,} records loaded.")
    except Exception as e:
        st.error(f"❌ Error: {e}")

df = st.session_state.df

# ── 5 tabs: EV / FUEL / HYBRID / Comparison / Charging Stations ─────────────
tab_ev, tab_fuel, tab_hybrid, tab_cmp, tab_cs = st.tabs([
    L["tab_ev"], L["tab_fuel"], L["tab_hybrid"], L["tab_compare"], L["tab_cs"]
])

with tab_ev:
    ev_trip = st.file_uploader(L["upload_trip"], type=["xml"], key="ev_trip")
    df_ev, df_ev_t, df_ev_e, df_ev_b = merge_outputs(ev_trip)
    fleet_panel(df_ev, df_ev_t, df_ev_e, df_ev_b, "EV", fiyat_yakit, fiyat_elec, curr_sym, conv)

with tab_fuel:
    fu_trip = st.file_uploader(L["upload_trip"], type=["xml"], key="fu_trip")
    df_fu, df_fu_t, df_fu_e, df_fu_b = merge_outputs(fu_trip)
    fleet_panel(df_fu, df_fu_t, df_fu_e, df_fu_b, "FUEL", fiyat_yakit, fiyat_elec, curr_sym, conv)

with tab_hybrid:
    hy_trip = st.file_uploader(L["upload_trip"], type=["xml"], key="hy_trip")
    df_hy, df_hy_t, df_hy_e, df_hy_b = merge_outputs(hy_trip)
    fleet_panel(df_hy, df_hy_t, df_hy_e, df_hy_b, "HYBRID", fiyat_yakit, fiyat_elec, curr_sym, conv)

with tab_cmp:
    comparison_panel(
        {
            "EV":     (df_ev,  df_ev_t,  df_ev_e,  df_ev_b),
            "FUEL":   (df_fu,  df_fu_t,  df_fu_e,  df_fu_b),
            "HYBRID": (df_hy,  df_hy_t,  df_hy_e,  df_hy_b),
        },
        fiyat_yakit, fiyat_elec, curr_sym, conv
    )

with tab_cs:
    st.markdown("### 🔌 Charging Station Analysis")

    # ── Two-column upload: CS output + optional tripinfo for route stats ──
    cu1, cu2 = st.columns([1, 1])
    with cu1:
        cs_xml_file = st.file_uploader(
            L.get("cs_upload_trip", "📂 Upload chargingstations_output.xml"),
            type=["xml"], key="cs_xml_upload",
            help="SUMO output: output/chargingstations_output.xml"
        )
    with cu2:
        cs_trip_file = st.file_uploader(
            "📂 Upload tripinfo.xml (optional — for route km stats)",
            type=["xml"], key="cs_trip_upload",
            help="Same tripinfo.xml used in EV tab — needed for cost/100 km calc"
        )

    df_cs_stations, df_cs_events, df_cs_veh = parse_cs_output(cs_xml_file)
    # Optional tripinfo for distance stats
    _, df_cs_t, _, _ = merge_outputs(cs_trip_file) if cs_trip_file else (None, pd.DataFrame(), None, None)

    if df_cs_stations.empty:
        st.info(L.get("cs_no_data", "Upload chargingstations_output.xml (SUMO → output/chargingstations_output.xml)."))
    else:
        # ── Key metrics — from chargingstations_output ──────────────────────
        n_stations      = len(df_cs_stations)
        vehicles_charged = len(df_cs_veh)
        total_charged   = df_cs_veh["total_charged_kwh"].sum()
        total_events    = df_cs_events["charged_kwh"].count() if not df_cs_events.empty else 0
        avg_charged_veh = total_charged / max(vehicles_charged, 1)
        top_station_kwh = df_cs_stations["total_charged_kwh"].max() if not df_cs_stations.empty else 0

        # Cost calculation
        cost_charged    = total_charged * fiyat_elec * conv
        cost_per_cs_kwh = fiyat_elec * conv

        # Total distance from tripinfo (if uploaded)
        total_km = df_cs_t["route_length_km"].sum() if not df_cs_t.empty and "route_length_km" in df_cs_t.columns else 0

        st.markdown("#### 📊 Charging Station Overview")
        k1, k2, k3, k4, k5, k6 = st.columns(6)
        k1.metric("⚡ Active Stations",       f"{n_stations:,}")
        k2.metric("🚗 Vehicles Charged",      f"{vehicles_charged:,}")
        k3.metric("🔌 Total Charged",         f"{total_charged:,.1f} kWh")
        k4.metric("📋 Total Events",          f"{total_events:,}")
        k5.metric("🔋 Avg per Vehicle",       f"{avg_charged_veh:.2f} kWh")
        k6.metric("🏆 Top Station",           f"{top_station_kwh:.1f} kWh")

        st.markdown("---")
        st.markdown("#### 💰 Charging Cost")
        cc1, cc2, cc3, cc4 = st.columns(4)
        cc1.metric(f"Unit Price ({curr_sym}/kWh)",   f"{cost_per_cs_kwh:.3f}")
        cc2.metric("Total Charging Cost",            f"{curr_sym}{cost_charged:,.2f}")
        cc3.metric("Cost / Charged Vehicle",         f"{curr_sym}{cost_charged/max(vehicles_charged,1):,.2f}")
        if total_km > 0:
            cc4.metric("Cost / 100 km", f"{curr_sym}{cost_charged / total_km * 100:,.2f}")
        else:
            cc4.metric("Cost / 100 km", "— upload tripinfo")

        # Electricity price override
        with st.expander("⚙️ Adjust Electricity Price for CS Analysis"):
            new_elec = st.number_input(
                f"Electricity price ({curr_sym}/kWh) — overrides sidebar value for this analysis",
                min_value=0.0, value=round(fiyat_elec*conv, 3), step=0.01, format="%.3f",
                key="cs_elec_override"
            )
            new_fiyat_elec = new_elec / conv
            cost_override = total_charged * new_fiyat_elec * conv
            st.metric("Recalculated Total Cost", f"{curr_sym}{cost_override:,.2f}",
                      delta=f"{curr_sym}{cost_override - cost_charged:+,.2f} vs sidebar price")
            if total_km > 0:
                st.metric("Recalculated Cost / 100 km",
                          f"{curr_sym}{cost_override / total_km * 100:,.2f}")

        st.markdown("---")
        st.markdown("#### ⚡ Energy by Station")
        df_top = df_cs_stations.nlargest(20, "total_charged_kwh")
        if PLOTLY_OK:
            fig_eb = go.Figure(go.Bar(
                x=df_top["station_id"],
                y=df_top["total_charged_kwh"],
                marker_color="#3498db",
                text=[f"{v:.1f}" for v in df_top["total_charged_kwh"]],
                textposition="outside"
            ))
            fig_eb.update_layout(
                height=340, margin=dict(t=20, b=80),
                xaxis_title="Station ID", yaxis_title="Total Charged (kWh)",
                xaxis_tickangle=-45, plot_bgcolor="rgba(0,0,0,0)"
            )
            st.plotly_chart(fig_eb, use_container_width=True)
        else:
            st.bar_chart(df_top.set_index("station_id")["total_charged_kwh"])

        st.markdown("---")
        st.markdown("#### 🔋 Charging Distribution")
        d1, d2 = st.columns(2)

        with d1:
            if not df_cs_veh.empty:
                if PLOTLY_OK:
                    fig_veh = go.Figure(go.Histogram(
                        x=df_cs_veh["total_charged_kwh"], nbinsx=25,
                        marker_color="#3498db", opacity=0.8
                    ))
                    fig_veh.update_layout(
                        title="Charged Energy per Vehicle (kWh)", height=280,
                        xaxis_title="kWh", yaxis_title="# Vehicles",
                        margin=dict(t=30, b=20), plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_veh, use_container_width=True)
                else:
                    st.bar_chart(df_cs_veh["total_charged_kwh"].value_counts().sort_index())

        with d2:
            if not df_cs_events.empty and "charge_begin_s" in df_cs_events.columns:
                durations = (df_cs_events["charge_end_s"] - df_cs_events["charge_begin_s"]).clip(lower=0)
                if PLOTLY_OK:
                    fig_dur = go.Figure(go.Histogram(
                        x=durations, nbinsx=25, marker_color="#2ecc71", opacity=0.8
                    ))
                    fig_dur.update_layout(
                        title="Charging Event Duration (s)", height=280,
                        xaxis_title="Duration (s)", yaxis_title="# Events",
                        margin=dict(t=30, b=20), plot_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_dur, use_container_width=True)
                else:
                    st.bar_chart(durations.value_counts().sort_index())

        # ── Per-station table ─────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("#### 📋 Per-Station Summary")
        df_st_disp = df_cs_stations.copy()
        df_st_disp["cost"] = df_st_disp["total_charged_kwh"] * fiyat_elec * conv
        df_st_disp.columns = ["Station ID", "Total Charged (kWh)", "# Events", f"Cost ({curr_sym})"]
        st.dataframe(
            df_st_disp.sort_values("Total Charged (kWh)", ascending=False),
            use_container_width=True, height=300
        )

        # ── Per-vehicle table ─────────────────────────────────────────────────
        st.markdown("#### 📋 Per-Vehicle Charging Summary")
        df_veh_disp = df_cs_veh.copy()
        df_veh_disp["cost"] = df_veh_disp["total_charged_kwh"] * fiyat_elec * conv
        # Merge tripinfo distance if available
        if not df_cs_t.empty and "route_length_km" in df_cs_t.columns and "vehicle_id" in df_cs_t.columns:
            df_veh_disp = df_veh_disp.merge(
                df_cs_t[["vehicle_id","route_length_km","avg_speed_kmh"]],
                on="vehicle_id", how="left"
            )
        df_veh_disp.rename(columns={
            "vehicle_id":         "Vehicle",
            "total_charged_kwh":  "Charged (kWh)",
            "n_stations_used":    "# Stations",
            "n_charge_events":    "# Events",
            "cost":               f"Cost ({curr_sym})",
            "route_length_km":    "Route (km)",
            "avg_speed_kmh":      "Avg Speed (km/h)",
        }, inplace=True)
        st.dataframe(
            df_veh_disp.sort_values("Charged (kWh)", ascending=False),
            use_container_width=True, height=320
        )

        # ── Raw events expander ───────────────────────────────────────────────
        with st.expander("🔍 Raw Charging Events"):
            st.dataframe(df_cs_events, use_container_width=True, height=300)