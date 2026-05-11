"""
VERA-NL: Verification Engine for Results & Accountability - Nederland
Type 4 Detectie: leerlingen wiens mondelinge Nederlands beter is dan schriftelijk (leraar-observatie)

Nederland heeft geen gestandaardiseerde ELP-toets. NT2 is schoolgebonden.
Doorstroomtoets (vervangt Cito Eindtoets vanaf 2024) in groep 8.
LVS-toetsen groep 3-8. Referentieniveaus: 1F/1S/2F/2S/3F/4F.
DUO open data (duo.nl). School-ID: BRIN (4-char).
~150 samenwerkingsverbanden (75 PO + 75 VO). ~2.6M leerlingen. ~30.000+ ISK/nieuwkomers.
ISK (Internationale Schakelklas) voor nieuwkomers in het voortgezet onderwijs.
LOWAN ondersteunt nieuwkomeronderwijs.

H-EDU.Solutions | https://h-edu.solutions
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ============================================================================
# CONFIGURATIE
# ============================================================================

APP_PASSWORD = "vera2026"

NL_ORANGE = "#FF6600"
NL_BLUE = "#003DA5"
NL_RED = "#CC0000"
NL_GREY = "#666666"
NL_GREEN = "#2E8B57"

# ============================================================================
# DATA: Samenwerkingsverbanden (SWV) met nieuwkomerpopulaties
# ============================================================================

def load_samenwerkingsverbanden():
    """Laad 15 pilot-samenwerkingsverbanden met nieuwkomerdata.
    Bron: DUO open data (duo.nl), Inspectie van het Onderwijs, CBS.
    SWV = samenwerkingsverband passend onderwijs.
    BRIN = Basis Registratie Instellingen (4-char school ID).
    Referentieniveaus: 1F (fundamenteel) / 1S (streef) / 2F / 3F.
    """
    data = [
        # (swv_code, swv_naam, regio, totaal_leerlingen, nieuwkomers, nieuwkomer_pct,
        #  pct_1f_lezen, pct_1s_lezen, pct_1f_taalverzorging, pct_1s_taalverzorging,
        #  pct_1f_rekenen, pct_1s_rekenen, isk_scholen, basisscholen)
        ("SWV2301", "Amsterdam-Diemen PO", "Amsterdam", 95000, 5200, 5.5, 96.2, 58.1, 94.8, 52.3, 95.1, 42.0, 12, 215),
        ("SWV2302", "Rotterdam PO", "Rotterdam", 72000, 4800, 6.7, 94.8, 54.2, 93.5, 48.9, 93.8, 38.5, 10, 178),
        ("SWV2303", "Den Haag PO", "Den Haag", 55000, 3600, 6.5, 95.0, 55.0, 93.8, 49.5, 94.0, 39.2, 8, 142),
        ("SWV2304", "Utrecht PO", "Utrecht", 48000, 2400, 5.0, 96.8, 61.5, 95.5, 55.8, 96.0, 46.3, 6, 128),
        ("SWV2305", "Almere PO", "Almere", 32000, 2100, 6.6, 94.5, 52.8, 93.2, 47.5, 93.5, 37.0, 5, 82),
        ("SWV2306", "Eindhoven PO", "Eindhoven", 38000, 1500, 3.9, 96.5, 60.2, 95.2, 54.8, 95.8, 44.5, 4, 98),
        ("SWV2307", "Groningen PO", "Groningen", 28000, 1200, 4.3, 96.0, 59.0, 95.0, 53.5, 95.5, 43.2, 3, 75),
        ("SWV2308", "Tilburg PO", "Tilburg", 25000, 1100, 4.4, 95.8, 57.8, 94.5, 52.0, 95.0, 41.8, 3, 68),
        ("SWV2309", "Arnhem-Nijmegen PO", "Arnhem", 42000, 1800, 4.3, 96.2, 59.5, 95.0, 53.8, 95.5, 43.8, 5, 110),
        ("SWV2310", "Zaanstad PO", "Zaanstad", 22000, 1400, 6.4, 94.2, 51.5, 93.0, 46.8, 93.2, 36.5, 3, 58),
        ("SWV2311", "Leiden PO", "Leiden", 18000, 800, 4.4, 97.0, 62.0, 96.0, 56.5, 96.5, 47.0, 2, 48),
        ("SWV2312", "Haarlem PO", "Haarlem", 20000, 750, 3.8, 97.2, 63.0, 96.2, 57.0, 96.8, 48.0, 2, 52),
        ("SWV2313", "Enschede PO", "Enschede", 19000, 950, 5.0, 95.5, 56.5, 94.2, 51.0, 94.5, 40.5, 3, 50),
        ("SWV2314", "Dordrecht PO", "Dordrecht", 16000, 900, 5.6, 95.0, 55.0, 93.8, 49.5, 94.0, 39.0, 2, 42),
        ("SWV2315", "Deventer PO", "Deventer", 14000, 650, 4.6, 96.0, 58.5, 95.0, 53.0, 95.2, 42.5, 2, 38),
    ]

    return pd.DataFrame(data, columns=[
        'swv_code', 'swv_naam', 'regio', 'totaal_leerlingen', 'nieuwkomers',
        'nieuwkomer_pct', 'pct_1f_lezen', 'pct_1s_lezen',
        'pct_1f_taalverzorging', 'pct_1s_taalverzorging',
        'pct_1f_rekenen', 'pct_1s_rekenen', 'isk_scholen', 'basisscholen'
    ])


# ============================================================================
# DATA: Referentieniveau-resultaten per regio
# ============================================================================

def load_referentieniveau_data(swv_df):
    """Genereer referentieniveau-resultaten per SWV en groep.
    Referentieniveaus: 1F (fundamenteel), 1S (streefniveau).
    LVS-toetsen meten voortgang groep 3-8.
    Doorstroomtoets in groep 8 bepaalt advies (VMBO/HAVO/VWO)."""
    ref_data = []

    for _, s in swv_df.iterrows():
        for groep in [3, 4, 5, 6, 7, 8]:
            for jaar in [2024, 2025]:
                groep_factor = (groep - 3) * 0.04
                jaar_factor = 0.005 if jaar == 2025 else 0.0

                # Nieuwkomers scoren lager op schriftelijke vaardigheden
                nk_penalty = s['nieuwkomer_pct'] * 0.8

                ref_data.append({
                    'swv_code': s['swv_code'],
                    'swv_naam': s['swv_naam'],
                    'regio': s['regio'],
                    'groep': groep,
                    'jaar': jaar,
                    'leerlingen_getoetst': max(50, int(s['totaal_leerlingen'] / 8)),
                    'pct_1f_lezen': round(min(99, s['pct_1f_lezen'] + groep_factor * 100 + jaar_factor * 100), 1),
                    'pct_1s_lezen': round(min(80, s['pct_1s_lezen'] + groep_factor * 60 + jaar_factor * 50), 1),
                    'pct_1f_taalverzorging': round(min(99, s['pct_1f_taalverzorging'] + groep_factor * 100 + jaar_factor * 100), 1),
                    'pct_1s_taalverzorging': round(min(75, s['pct_1s_taalverzorging'] + groep_factor * 50 + jaar_factor * 50), 1),
                    'pct_1f_rekenen': round(min(99, s['pct_1f_rekenen'] + groep_factor * 100 + jaar_factor * 100), 1),
                    'pct_1s_rekenen': round(min(70, s['pct_1s_rekenen'] + groep_factor * 50 + jaar_factor * 50), 1),
                    'mondeling_score': round(min(5.0, 3.2 + groep_factor * 10 - nk_penalty * 0.02 + 0.6), 2),
                    'schriftelijk_score': round(min(5.0, 2.5 + groep_factor * 8 - nk_penalty * 0.05), 2),
                })

    return pd.DataFrame(ref_data)


# ============================================================================
# DATA: NT2/Nieuwkomer ISK-data
# ============================================================================

def load_nieuwkomer_data(swv_df):
    """Genereer ISK/nieuwkomer-inschrijvingsdata per regio.
    ISK = Internationale Schakelklas (voortgezet onderwijs, 12-18 jaar).
    Nieuwkomers in PO: schakelklas of taalondersteuning in reguliere klas.
    Herkomstlanden: Oekraine, Syrie, Eritrea, Afghanistan, Turkije, Marokko, Polen, Bulgarije."""
    nk_data = []

    herkomst_verdeling = {
        'Oekraine': 0.22, 'Syrie': 0.18, 'Eritrea': 0.10, 'Afghanistan': 0.08,
        'Turkije': 0.12, 'Marokko': 0.10, 'Polen': 0.08, 'Bulgarije': 0.05,
        'Overig EU': 0.04, 'Overig niet-EU': 0.03
    }

    for _, s in swv_df.iterrows():
        for jaar in [2024, 2025]:
            nk_basis = s['nieuwkomers']
            if jaar == 2025:
                nk_basis = int(nk_basis * 1.08)  # 8% groei

            for herkomst, pct in herkomst_verdeling.items():
                nk_data.append({
                    'swv_code': s['swv_code'],
                    'swv_naam': s['swv_naam'],
                    'regio': s['regio'],
                    'jaar': jaar,
                    'herkomstland': herkomst,
                    'aantal': int(nk_basis * pct),
                    'isk_inschrijvingen': int(nk_basis * pct * 0.4),
                    'schakelklas_po': int(nk_basis * pct * 0.35),
                    'regulier_met_steun': int(nk_basis * pct * 0.25),
                })

    return pd.DataFrame(nk_data)


# ============================================================================
# DATA: Doorstroomtoets adviezen
# ============================================================================

def load_doorstroomtoets_data(swv_df):
    """Genereer Doorstroomtoets-adviesdata per SWV.
    Doorstroomtoets (vervangt Cito Eindtoets vanaf feb 2024) in groep 8.
    Advies kan alleen OMHOOG bijgesteld worden op basis van toetsresultaat.
    Adviesniveaus: VMBO-basis, VMBO-kader, VMBO-t (theoretisch), HAVO, VWO.
    Achtergrondkenmerken: SES (opleidingsniveau ouders), migratieachtergrond."""
    dt_data = []

    for _, s in swv_df.iterrows():
        for jaar in [2024, 2025]:
            nk_pct = s['nieuwkomer_pct']
            ses_factor = s['pct_1s_lezen'] / 60.0  # Proxy voor SES via leesprestaties

            # Adviesniveaus (percentages)
            vwo_pct = round(max(5, 18 * ses_factor - nk_pct * 0.3), 1)
            havo_pct = round(max(8, 22 * ses_factor - nk_pct * 0.2), 1)
            vmbo_t_pct = round(max(10, 25 - (ses_factor - 1) * 5), 1)
            vmbo_k_pct = round(max(8, 20 - (ses_factor - 1) * 3 + nk_pct * 0.2), 1)
            vmbo_b_pct = round(100 - vwo_pct - havo_pct - vmbo_t_pct - vmbo_k_pct, 1)

            # Bijstellingen omhoog
            bijstelling_pct = round(max(3, 12 - ses_factor * 3 + nk_pct * 0.5), 1)

            groep8_leerlingen = int(s['totaal_leerlingen'] / 8)

            dt_data.append({
                'swv_code': s['swv_code'],
                'swv_naam': s['swv_naam'],
                'regio': s['regio'],
                'jaar': jaar,
                'groep8_leerlingen': groep8_leerlingen,
                'vwo_pct': vwo_pct,
                'havo_pct': havo_pct,
                'vmbo_t_pct': vmbo_t_pct,
                'vmbo_k_pct': vmbo_k_pct,
                'vmbo_b_pct': vmbo_b_pct,
                'bijstelling_omhoog_pct': bijstelling_pct,
                'nieuwkomer_pct': nk_pct,
            })

            # Subgroepen
            for subgroep, adj in [
                ('Geen migratieachtergrond', 1.15),
                ('Westerse migratieachtergrond', 0.95),
                ('Niet-westerse migratieachtergrond', 0.75),
                ('Nieuwkomer (<3 jaar in NL)', 0.55),
            ]:
                dt_data.append({
                    'swv_code': s['swv_code'],
                    'swv_naam': s['swv_naam'],
                    'regio': s['regio'],
                    'jaar': jaar,
                    'groep8_leerlingen': int(groep8_leerlingen * (0.4 if 'Geen' in subgroep else 0.15 if 'Westers' in subgroep and 'Niet' not in subgroep else 0.35 if 'Niet' in subgroep else 0.10)),
                    'vwo_pct': round(max(2, vwo_pct * adj), 1),
                    'havo_pct': round(max(4, havo_pct * adj), 1),
                    'vmbo_t_pct': round(vmbo_t_pct * (2 - adj) * 0.9, 1),
                    'vmbo_k_pct': round(vmbo_k_pct * (2 - adj), 1),
                    'vmbo_b_pct': round(max(5, vmbo_b_pct * (2 - adj) * 1.1), 1),
                    'bijstelling_omhoog_pct': round(max(2, bijstelling_pct * (2 - adj)), 1),
                    'nieuwkomer_pct': nk_pct,
                    'subgroep': subgroep,
                })

    df = pd.DataFrame(dt_data)
    df['subgroep'] = df['subgroep'].fillna('Alle leerlingen')
    return df


# ============================================================================
# DATA: Landelijke referentieniveau-verdeling
# ============================================================================

def load_landelijke_referentieniveaus():
    """Landelijke referentieniveau-resultaten einde basisschool.
    Bron: Inspectie van het Onderwijs, Staat van het Onderwijs.
    1F = fundamenteel niveau (behaald door vrijwel alle leerlingen).
    1S/2F = streefniveau (target voor einde basisschool, ~55-65% haalt dit)."""
    return pd.DataFrame([
        {'jaar': '2024-25', 'domein': 'Lezen', 'pct_1f': 96.5, 'pct_1s_2f': 60.2, 'pct_beneden_1f': 3.5},
        {'jaar': '2024-25', 'domein': 'Taalverzorging', 'pct_1f': 95.0, 'pct_1s_2f': 53.8, 'pct_beneden_1f': 5.0},
        {'jaar': '2024-25', 'domein': 'Rekenen', 'pct_1f': 95.5, 'pct_1s_2f': 43.5, 'pct_beneden_1f': 4.5},
        {'jaar': '2023-24', 'domein': 'Lezen', 'pct_1f': 96.0, 'pct_1s_2f': 58.5, 'pct_beneden_1f': 4.0},
        {'jaar': '2023-24', 'domein': 'Taalverzorging', 'pct_1f': 94.5, 'pct_1s_2f': 52.0, 'pct_beneden_1f': 5.5},
        {'jaar': '2023-24', 'domein': 'Rekenen', 'pct_1f': 95.0, 'pct_1s_2f': 42.0, 'pct_beneden_1f': 5.0},
    ])


# ============================================================================
# AUTHENTICATIE
# ============================================================================

def check_password():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True

    st.markdown(f"""
    <div style="text-align: center; padding: 60px 20px;">
        <h1 style="color: {NL_ORANGE}; font-size: 3rem; margin-bottom: 10px;">VERA-NL</h1>
        <p style="color: #666; font-size: 1.1rem; margin-bottom: 40px;">
            Verification Engine for Results &amp; Accountability<br>Nederland Implementatie
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        password = st.text_input("Voer toegangscode in:", type="password", key="pw")
        if st.button("Toegang tot VERA-NL", use_container_width=True):
            if password == APP_PASSWORD:
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Ongeldige toegangscode")

    st.markdown(f"""
    <div style="text-align: center; margin-top: 60px; color: #999; font-size: 0.85rem;">
        <p>VERA-NL analyseert referentieniveaus, doorstroomtoets-adviezen en nieuwkomerdata over 15 pilot-samenwerkingsverbanden.</p>
        <p>~2.6 miljoen leerlingen | ~30.000+ nieuwkomers | Referentieniveaus 1F/1S/2F</p>
        <p style="margin-top: 10px;">Contact: brian@h-edu.solutions</p>
    </div>
    """, unsafe_allow_html=True)
    return False


# ============================================================================
# TYPE 4 DETECTIE
# ============================================================================

def compute_type4_analysis(ref_df, swv_code, groep, jaar):
    """Type 4 detectie: leerlingen wiens mondelinge Nederlands beter is dan schriftelijk.
    In Nederland is er geen gestandaardiseerde orale toets; dit is gebaseerd op
    leraar-observatie (mondeling) vs LVS-toetsen (schriftelijk).
    Delta = mondeling_score - schriftelijk_score (schaal 1-5).
    Vlag-drempel: delta > 0.7 (betekenisvolle kloof mondeling-schriftelijk)."""
    filtered = ref_df[
        (ref_df['swv_code'] == swv_code) & (ref_df['groep'] == groep) & (ref_df['jaar'] == jaar)
    ]
    if filtered.empty:
        return None

    row = filtered.iloc[0]
    delta = row['mondeling_score'] - row['schriftelijk_score']
    flagged = delta > 0.7

    return {
        'swv_code': swv_code, 'swv_naam': row['swv_naam'],
        'regio': row['regio'], 'groep': groep, 'jaar': jaar,
        'mondeling_score': row['mondeling_score'],
        'schriftelijk_score': row['schriftelijk_score'],
        'delta': delta, 'flagged': flagged,
        'leerlingen_getoetst': row['leerlingen_getoetst'],
        'geschat_gevlagd': int(row['leerlingen_getoetst'] * 0.12) if flagged else int(row['leerlingen_getoetst'] * 0.04)
    }


# ============================================================================
# PAGINA'S
# ============================================================================

def render_overview(swv_df):
    st.header("Nederland Onderwijs Overzicht")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Pilot SWV's", len(swv_df))
    with col2:
        st.metric("Totaal Leerlingen", f"{swv_df['totaal_leerlingen'].sum():,}")
    with col3:
        st.metric("Nieuwkomers", f"{swv_df['nieuwkomers'].sum():,}")
    with col4:
        st.metric("ISK-scholen", f"{swv_df['isk_scholen'].sum()}", help="Internationale Schakelklassen in pilotregio's")

    st.divider()

    st.subheader("Nederlands Onderwijsstelsel - Context")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("**~150 Samenwerkingsverbanden**\n75 PO (primair onderwijs) + 75 VO (voortgezet onderwijs)")
    with col2:
        st.warning("**~30.000+ Nieuwkomers**\nSterke toename door immigratie, met name uit Oekraine")
    with col3:
        st.error("**Doorstroomtoets (2024)**\nVervangt Cito Eindtoets, kan advies alleen OMHOOG bijstellen")

    st.divider()

    st.subheader("Onderwijscontext")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **Referentieniveaus**
        - 1F = fundamenteel niveau (minimum, einde basisschool)
        - 1S/2F = streefniveau (target einde basisschool)
        - 2F = functioneel niveau (target einde VMBO/HAVO)
        - 3F/4F = hogere niveaus (HAVO/VWO/hoger onderwijs)
        - Domeinen: Lezen, Taalverzorging, Rekenen
        """)
    with col2:
        st.markdown("""
        **Nieuwkomeronderwijs**
        - ISK (Internationale Schakelklas): VO, 12-18 jaar
        - Schakelklas (PO): extra taalondersteuning basisschool
        - NT2 (Nederlands als Tweede Taal): schoolgebonden
        - LOWAN: landelijke ondersteuning nieuwkomeronderwijs
        - Geen gestandaardiseerde ELP-toets landelijk
        """)

    st.divider()

    st.subheader("Immigratiegolf en Nieuwkomeronderwijs")
    st.markdown("""
    Nederland heeft sinds 2022 een sterke toename van nieuwkomerleerlingen, voornamelijk door:
    - **Oekraine-crisis**: Grootste groep nieuwe instromers (22%)
    - **Asielinstroom**: Syrie, Eritrea, Afghanistan
    - **EU-arbeidsmigratie**: Polen, Bulgarije, Roemenie
    - **Gezinshereniging**: Turkije, Marokko

    De capaciteit van ISK-scholen en schakelklassen staat onder druk. Wachtlijsten in grote steden.
    """)

    st.divider()

    st.subheader("Pilot-Samenwerkingsverbanden")
    display = swv_df[['swv_code', 'swv_naam', 'regio', 'totaal_leerlingen', 'nieuwkomers',
                       'nieuwkomer_pct', 'isk_scholen', 'basisscholen']].copy()
    display.columns = ['SWV Code', 'Naam', 'Regio', 'Leerlingen', 'Nieuwkomers',
                       'Nieuwkomer %', 'ISK-scholen', 'Basisscholen']
    st.dataframe(display, use_container_width=True, hide_index=True)

    st.subheader("Nieuwkomerpopulatie per Samenwerkingsverband")
    fig = px.bar(
        swv_df.sort_values('nieuwkomers', ascending=True),
        x='nieuwkomers', y='swv_naam', orientation='h',
        color='nieuwkomer_pct', color_continuous_scale=[[0, '#C0C0C0'], [1, NL_ORANGE]],
        labels={'nieuwkomers': 'Nieuwkomers', 'swv_naam': 'Samenwerkingsverband', 'nieuwkomer_pct': 'Nieuwkomer %'}
    )
    fig.update_layout(height=550, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # SWV kaart (simpele weergave)
    st.subheader("Regionale Spreiding")
    kaart_data = swv_df[['regio', 'nieuwkomers', 'nieuwkomer_pct']].copy()
    kaart_data = kaart_data.sort_values('nieuwkomers', ascending=False)

    fig_kaart = px.treemap(
        kaart_data, path=['regio'], values='nieuwkomers',
        color='nieuwkomer_pct', color_continuous_scale=[[0, '#FFE0B2'], [1, NL_ORANGE]],
        labels={'nieuwkomers': 'Nieuwkomers', 'nieuwkomer_pct': 'Nieuwkomer %'}
    )
    fig_kaart.update_layout(title="Nieuwkomers per Regio (treemap)", height=400)
    st.plotly_chart(fig_kaart, use_container_width=True)


def render_referentieniveau(ref_df, landelijk_df):
    st.header("Referentieniveau Analyse")

    st.markdown("""
    **Referentieniveaus** vormen de kern van het Nederlandse onderwijsstelsel.
    LVS-toetsen (Leerling Volg Systeem) meten voortgang van groep 3 t/m 8.
    1F = fundamenteel niveau (minimum), 1S/2F = streefniveau.
    Bron: DUO open data, Inspectie van het Onderwijs.
    """)

    # Landelijke data
    st.subheader("Landelijke Referentieniveau-resultaten")
    jaar_l = st.selectbox("Jaar", ['2024-25', '2023-24'], key="ref_landelijk_j")
    filtered_l = landelijk_df[landelijk_df['jaar'] == jaar_l]

    col1, col2, col3 = st.columns(3)
    for i, (_, row) in enumerate(filtered_l.iterrows()):
        with [col1, col2, col3][i]:
            st.metric(f"{row['domein']} - 1F behaald", f"{row['pct_1f']}%")
            st.metric(f"{row['domein']} - 1S/2F behaald", f"{row['pct_1s_2f']}%")
            st.metric(f"{row['domein']} - Beneden 1F", f"{row['pct_beneden_1f']}%")

    st.divider()

    fig_l = go.Figure()
    for col_name, label, color in [
        ('pct_1f', 'Behaald 1F', NL_BLUE),
        ('pct_1s_2f', 'Behaald 1S/2F', NL_ORANGE),
        ('pct_beneden_1f', 'Beneden 1F', NL_RED),
    ]:
        fig_l.add_trace(go.Bar(
            x=filtered_l['domein'], y=filtered_l[col_name],
            name=label, marker_color=color,
            text=[f"{v}%" for v in filtered_l[col_name]], textposition='outside'
        ))
    fig_l.update_layout(
        title=f"Landelijke Referentieniveau-resultaten ({jaar_l})",
        xaxis_title="Domein", yaxis_title="%",
        barmode='group', height=450, yaxis=dict(range=[0, 105])
    )
    st.plotly_chart(fig_l, use_container_width=True)

    st.divider()

    # Per SWV
    st.subheader("Referentieniveaus per Samenwerkingsverband")
    col1, col2, col3 = st.columns(3)
    with col1:
        regio = st.selectbox("Regio", ref_df['regio'].unique().tolist(), key="ref_r")
    with col2:
        groep = st.selectbox("Groep", [3, 4, 5, 6, 7, 8], index=5, key="ref_g")
    with col3:
        jaar = st.selectbox("Jaar", [2025, 2024], key="ref_j")

    filtered = ref_df[(ref_df['regio'] == regio) & (ref_df['groep'] == groep) & (ref_df['jaar'] == jaar)]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Lezen - 1F", f"{row['pct_1f_lezen']}%")
            st.metric("Lezen - 1S", f"{row['pct_1s_lezen']}%")
        with col2:
            st.metric("Taalverzorging - 1F", f"{row['pct_1f_taalverzorging']}%")
            st.metric("Taalverzorging - 1S", f"{row['pct_1s_taalverzorging']}%")
        with col3:
            st.metric("Rekenen - 1F", f"{row['pct_1f_rekenen']}%")
            st.metric("Rekenen - 1S", f"{row['pct_1s_rekenen']}%")

        # Vergelijking 1F vs 1S per domein
        domeinen = ['Lezen', 'Taalverzorging', 'Rekenen']
        pct_1f = [row['pct_1f_lezen'], row['pct_1f_taalverzorging'], row['pct_1f_rekenen']]
        pct_1s = [row['pct_1s_lezen'], row['pct_1s_taalverzorging'], row['pct_1s_rekenen']]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=domeinen, y=pct_1f, name='1F (fundamenteel)',
            marker_color=NL_BLUE,
            text=[f"{v}%" for v in pct_1f], textposition='outside'
        ))
        fig.add_trace(go.Bar(
            x=domeinen, y=pct_1s, name='1S (streef)',
            marker_color=NL_ORANGE,
            text=[f"{v}%" for v in pct_1s], textposition='outside'
        ))
        fig.update_layout(
            title=f"Referentieniveaus -- {regio} -- Groep {groep} ({jaar})",
            yaxis_title="% leerlingen dat niveau behaalt",
            barmode='group', height=450, yaxis=dict(range=[0, 110])
        )
        st.plotly_chart(fig, use_container_width=True)

    # Vergelijking alle regio's
    st.subheader(f"Vergelijking alle regio's -- Groep {groep} ({jaar})")
    all_regions = ref_df[(ref_df['groep'] == groep) & (ref_df['jaar'] == jaar)].sort_values('pct_1s_lezen', ascending=True)
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=all_regions['regio'], x=all_regions['pct_1s_lezen'],
        name='Lezen 1S', marker_color=NL_BLUE, orientation='h'
    ))
    fig2.add_trace(go.Bar(
        y=all_regions['regio'], x=all_regions['pct_1s_taalverzorging'],
        name='Taalverzorging 1S', marker_color=NL_ORANGE, orientation='h'
    ))
    fig2.add_trace(go.Bar(
        y=all_regions['regio'], x=all_regions['pct_1s_rekenen'],
        name='Rekenen 1S', marker_color=NL_GREEN, orientation='h'
    ))
    fig2.update_layout(
        title=f"1S/Streefniveau per Regio -- Groep {groep} ({jaar})",
        xaxis_title="% behaald 1S", barmode='group', height=550
    )
    st.plotly_chart(fig2, use_container_width=True)


def render_nieuwkomer_analyse(nk_df, swv_df):
    st.header("NT2 / Nieuwkomer Analyse")

    st.markdown("""
    **Nieuwkomeronderwijs in Nederland:**
    - ISK (Internationale Schakelklas): voortgezet onderwijs, 12-18 jaar
    - Schakelklas (PO): extra taalondersteuning in het basisonderwijs
    - NT2 (Nederlands als Tweede Taal): schoolgebonden taalprogramma
    - LOWAN: landelijke ondersteuning nieuwkomeronderwijs
    - Geen gestandaardiseerde landelijke ELP-toets
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Totaal Nieuwkomers (pilot)", f"{swv_df['nieuwkomers'].sum():,}")
    with col2:
        st.metric("ISK-scholen (pilot)", f"{swv_df['isk_scholen'].sum()}")
    with col3:
        st.metric("Gem. Nieuwkomer %", f"{swv_df['nieuwkomer_pct'].mean():.1f}%")
    with col4:
        st.metric("Basisscholen (pilot)", f"{swv_df['basisscholen'].sum():,}")

    st.divider()

    jaar = st.selectbox("Jaar", [2025, 2024], key="nk_j")
    nk_jaar = nk_df[nk_df['jaar'] == jaar]

    # Herkomst verdeling
    st.subheader(f"Nieuwkomers naar Herkomstland ({jaar})")
    herkomst_totaal = nk_jaar.groupby('herkomstland')['aantal'].sum().reset_index()
    herkomst_totaal = herkomst_totaal.sort_values('aantal', ascending=False)

    fig = px.bar(
        herkomst_totaal, x='herkomstland', y='aantal',
        color='aantal', color_continuous_scale=[[0, '#FFE0B2'], [1, NL_ORANGE]],
        labels={'herkomstland': 'Herkomstland', 'aantal': 'Aantal Nieuwkomers'}
    )
    fig.update_layout(title=f"Nieuwkomers naar Herkomstland ({jaar})", height=400, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    # Verdeling ISK / Schakelklas / Regulier
    st.subheader("Verdeling Onderwijstype Nieuwkomers")
    regio_nk = nk_jaar.groupby('regio').agg({
        'isk_inschrijvingen': 'sum',
        'schakelklas_po': 'sum',
        'regulier_met_steun': 'sum',
        'aantal': 'sum'
    }).reset_index().sort_values('aantal', ascending=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        y=regio_nk['regio'], x=regio_nk['isk_inschrijvingen'],
        name='ISK (VO)', marker_color=NL_BLUE, orientation='h'
    ))
    fig2.add_trace(go.Bar(
        y=regio_nk['regio'], x=regio_nk['schakelklas_po'],
        name='Schakelklas (PO)', marker_color=NL_ORANGE, orientation='h'
    ))
    fig2.add_trace(go.Bar(
        y=regio_nk['regio'], x=regio_nk['regulier_met_steun'],
        name='Regulier met steun', marker_color=NL_GREEN, orientation='h'
    ))
    fig2.update_layout(
        title="Verdeling Onderwijstype per Regio",
        xaxis_title="Aantal Nieuwkomers", barmode='stack', height=550
    )
    st.plotly_chart(fig2, use_container_width=True)

    # Per regio detail
    st.subheader("Nieuwkomers per Regio en Herkomst")
    regio_sel = st.selectbox("Selecteer Regio", swv_df['regio'].tolist(), key="nk_r")
    regio_detail = nk_jaar[nk_jaar['regio'] == regio_sel]
    if not regio_detail.empty:
        fig3 = px.pie(
            regio_detail, values='aantal', names='herkomstland',
            title=f"Herkomstverdeling -- {regio_sel} ({jaar})",
            color_discrete_sequence=px.colors.sequential.Oranges_r
        )
        fig3.update_layout(height=400)
        st.plotly_chart(fig3, use_container_width=True)

    # Groei
    st.subheader("Groei Nieuwkomerpopulatie 2024-2025")
    nk_2024 = nk_df[nk_df['jaar'] == 2024].groupby('regio')['aantal'].sum().reset_index()
    nk_2025 = nk_df[nk_df['jaar'] == 2025].groupby('regio')['aantal'].sum().reset_index()
    groei = nk_2024.merge(nk_2025, on='regio', suffixes=('_2024', '_2025'))
    groei['groei_pct'] = round((groei['aantal_2025'] - groei['aantal_2024']) / groei['aantal_2024'] * 100, 1)
    groei = groei.sort_values('groei_pct', ascending=True)

    fig4 = go.Figure(go.Bar(
        y=groei['regio'], x=groei['groei_pct'], orientation='h',
        marker_color=[NL_RED if g > 10 else NL_ORANGE for g in groei['groei_pct']],
        text=[f"{g:+.1f}%" for g in groei['groei_pct']], textposition='outside'
    ))
    fig4.update_layout(title="Groei Nieuwkomerpopulatie 2024-2025 (%)", xaxis_title="Groei %", height=500)
    st.plotly_chart(fig4, use_container_width=True)


def render_type4(ref_df, swv_df):
    st.header("Type 4 Detectie")

    st.markdown("""
    **Type 4 kandidaten:** leerlingen wiens mondelinge Nederlands (spreken, luisteren)
    sterker is dan hun schriftelijke vaardigheden (lezen, schrijven).

    **Nederlandse context:** Er is geen gestandaardiseerde orale taaltoets.
    Type 4 detectie is gebaseerd op:
    - **Mondeling:** Leraar-observatie (schaal 1-5)
    - **Schriftelijk:** LVS-toetsen (Lezen, Taalverzorging)
    - **Delta:** Mondeling - Schriftelijk score
    - **Vlag-drempel:** delta > 0.7 punten
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        regio = st.selectbox("Regio", swv_df['regio'].tolist(), key="t4_r")
    with col2:
        groep = st.selectbox("Groep", [3, 4, 5, 6, 7, 8], key="t4_g")
    with col3:
        jaar = st.selectbox("Jaar", [2025, 2024], key="t4_j")

    swv_code = swv_df[swv_df['regio'] == regio]['swv_code'].values[0]
    result = compute_type4_analysis(ref_df, swv_code, groep, jaar)

    if result:
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mondeling Score", f"{result['mondeling_score']:.2f}")
        with col2:
            st.metric("Schriftelijk Score", f"{result['schriftelijk_score']:.2f}")
        with col3:
            st.metric("Delta", f"{result['delta']:+.2f}")
        with col4:
            st.metric("Status", "GEVLAGD" if result['flagged'] else "OK")

        fig = go.Figure()
        fig.add_trace(go.Bar(
            name='Mondeling (leraar-observatie)', x=['Score'],
            y=[result['mondeling_score']], marker_color=NL_ORANGE
        ))
        fig.add_trace(go.Bar(
            name='Schriftelijk (LVS-toets)', x=['Score'],
            y=[result['schriftelijk_score']], marker_color=NL_BLUE
        ))
        fig.update_layout(
            title=f"Mondeling vs Schriftelijk -- {regio} -- Groep {groep}",
            barmode='group', height=350, yaxis=dict(range=[0, 5.5]),
            yaxis_title="Score (1-5)"
        )
        st.plotly_chart(fig, use_container_width=True)

        if result['flagged']:
            st.error(f"**Type 4 Vlag Getriggerd** -- Delta: {result['delta']:+.2f}. "
                     f"Geschat {result['geschat_gevlagd']} van {result['leerlingen_getoetst']} leerlingen betreft.")
        else:
            st.success(f"**Geen Type 4 Vlag** -- Delta binnen normaal bereik ({result['delta']:+.2f}).")

        # Alle groepen
        st.subheader(f"Alle Groepen -- {regio} ({jaar})")
        all_data = [compute_type4_analysis(ref_df, swv_code, g, jaar) for g in [3, 4, 5, 6, 7, 8]]
        all_data = [r for r in all_data if r]
        if all_data:
            gdf = pd.DataFrame(all_data)
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=gdf['groep'], y=gdf['mondeling_score'], name='Mondeling',
                mode='lines+markers', line=dict(color=NL_ORANGE, width=3)
            ))
            fig2.add_trace(go.Scatter(
                x=gdf['groep'], y=gdf['schriftelijk_score'], name='Schriftelijk',
                mode='lines+markers', line=dict(color=NL_BLUE, width=3)
            ))
            fig2.update_layout(
                title="Mondeling vs Schriftelijk over Groepen",
                xaxis_title="Groep", yaxis_title="Score (1-5)",
                height=400, yaxis=dict(range=[0, 5.5])
            )
            st.plotly_chart(fig2, use_container_width=True)

    # Alle regio's overzicht
    st.divider()
    st.subheader(f"Type 4 Overzicht Alle Regio's -- Groep {groep} ({jaar})")
    all_regions = []
    for _, s in swv_df.iterrows():
        r = compute_type4_analysis(ref_df, s['swv_code'], groep, jaar)
        if r:
            all_regions.append(r)
    if all_regions:
        ardf = pd.DataFrame(all_regions).sort_values('delta', ascending=False)
        fig3 = go.Figure(go.Bar(
            x=ardf['regio'], y=ardf['delta'],
            marker_color=[NL_RED if f else NL_GREEN for f in ardf['flagged']],
            text=[f"{d:+.2f}" for d in ardf['delta']], textposition='outside'
        ))
        fig3.add_hline(y=0.7, line_dash="dash", line_color="red",
                       annotation_text="Vlag-drempel (0.7)")
        fig3.update_layout(
            title=f"Mondeling-Schriftelijk Delta per Regio -- Groep {groep}",
            yaxis_title="Delta", height=450
        )
        st.plotly_chart(fig3, use_container_width=True)


def render_achievement_gaps(dt_df, swv_df):
    st.header("Prestatiekloof Analyse")

    st.markdown("""
    **Doorstroomtoets adviesniveau-verdeling naar achtergrond.**
    De doorstroomtoets kan het schooladvies alleen OMHOOG bijstellen.
    Achtergrondkenmerken: migratieachtergrond, SES (opleidingsniveau ouders).
    Adviesniveaus: VMBO-basis, VMBO-kader, VMBO-t, HAVO, VWO.
    """)

    col1, col2 = st.columns(2)
    with col1:
        regio = st.selectbox("Regio", swv_df['regio'].tolist(), key="gap_r")
    with col2:
        jaar = st.selectbox("Jaar", [2025, 2024], key="gap_j")

    swv_code = swv_df[swv_df['regio'] == regio]['swv_code'].values[0]
    filtered = dt_df[(dt_df['swv_code'] == swv_code) & (dt_df['jaar'] == jaar)]

    if not filtered.empty:
        st.divider()

        # Vergelijking subgroepen
        st.subheader(f"Adviesverdeling naar Achtergrond -- {regio} ({jaar})")
        subgroepen = filtered[filtered['subgroep'] != 'Alle leerlingen'].copy()

        if not subgroepen.empty:
            niveaus = ['vmbo_b_pct', 'vmbo_k_pct', 'vmbo_t_pct', 'havo_pct', 'vwo_pct']
            labels = ['VMBO-basis', 'VMBO-kader', 'VMBO-t', 'HAVO', 'VWO']
            kleuren = [NL_RED, '#E8540A', NL_GREY, NL_ORANGE, NL_BLUE]

            fig = go.Figure()
            for niveau, label, kleur in zip(niveaus, labels, kleuren):
                fig.add_trace(go.Bar(
                    y=subgroepen['subgroep'], x=subgroepen[niveau],
                    name=label, marker_color=kleur, orientation='h',
                    text=[f"{v:.0f}%" for v in subgroepen[niveau]], textposition='inside'
                ))
            fig.update_layout(
                barmode='stack', height=400,
                title=f"Doorstroomtoets Adviesverdeling -- {regio}",
                xaxis_title="Percentage"
            )
            st.plotly_chart(fig, use_container_width=True)

            # HAVO/VWO percentages vergelijking
            st.subheader("HAVO + VWO Advies naar Achtergrond")
            subgroepen['havo_vwo_pct'] = subgroepen['havo_pct'] + subgroepen['vwo_pct']
            fig2 = go.Figure(go.Bar(
                x=subgroepen['subgroep'], y=subgroepen['havo_vwo_pct'],
                marker_color=[NL_BLUE, NL_ORANGE, NL_RED, '#8B0000'],
                text=[f"{v:.1f}%" for v in subgroepen['havo_vwo_pct']], textposition='outside'
            ))
            fig2.update_layout(
                title="% Leerlingen met HAVO/VWO Advies",
                yaxis_title="HAVO + VWO %", height=400
            )
            st.plotly_chart(fig2, use_container_width=True)

            # Bijstelling omhoog
            st.subheader("Bijstelling Omhoog door Doorstroomtoets")
            st.markdown("""
            De doorstroomtoets kan het schooladvies alleen **omhoog** bijstellen.
            Hogere bijstellingspercentages bij achterstandsgroepen duiden mogelijk op
            conservatieve initiële adviezen.
            """)
            fig3 = go.Figure(go.Bar(
                x=subgroepen['subgroep'], y=subgroepen['bijstelling_omhoog_pct'],
                marker_color=[NL_GREEN, NL_ORANGE, NL_RED, '#8B0000'],
                text=[f"{v:.1f}%" for v in subgroepen['bijstelling_omhoog_pct']], textposition='outside'
            ))
            fig3.update_layout(
                title="% Bijstelling Omhoog per Achtergrond",
                yaxis_title="Bijstelling Omhoog %", height=400
            )
            st.plotly_chart(fig3, use_container_width=True)

    # Alle regio's vergelijking
    st.divider()
    st.subheader(f"Prestatiekloof Alle Regio's ({jaar})")
    alle_regio = dt_df[(dt_df['jaar'] == jaar) & (dt_df['subgroep'] == 'Alle leerlingen')].copy()
    if not alle_regio.empty:
        alle_regio['havo_vwo_pct'] = alle_regio['havo_pct'] + alle_regio['vwo_pct']
        alle_regio = alle_regio.sort_values('havo_vwo_pct', ascending=True)

        fig4 = px.scatter(
            alle_regio, x='havo_vwo_pct', y='bijstelling_omhoog_pct',
            size='groep8_leerlingen', color='nieuwkomer_pct',
            color_continuous_scale=[[0, '#ccc'], [1, NL_ORANGE]],
            hover_name='regio',
            labels={
                'havo_vwo_pct': 'HAVO/VWO Advies %',
                'bijstelling_omhoog_pct': 'Bijstelling Omhoog %',
                'groep8_leerlingen': 'Groep 8 Leerlingen',
                'nieuwkomer_pct': 'Nieuwkomer %'
            }
        )
        fig4.update_layout(
            title="HAVO/VWO Advies vs Bijstelling Omhoog per Regio",
            height=450
        )
        st.plotly_chart(fig4, use_container_width=True)


def render_doorstroomtoets(dt_df, swv_df):
    st.header("Doorstroomtoets Analyse")

    st.markdown("""
    **Doorstroomtoets** (vervangt Cito Eindtoets vanaf februari 2024).
    Groep 8 leerlingen maken de toets na het schooladvies.
    De toets kan het advies alleen **OMHOOG** bijstellen, nooit omlaag.
    Adviesniveaus: VMBO-basis, VMBO-kader, VMBO-t (theoretisch), HAVO, VWO.
    Meerdere aanbieders: AMN, IEP, Dia, Route 8.
    """)

    col1, col2 = st.columns(2)
    with col1:
        regio = st.selectbox("Regio", swv_df['regio'].tolist(), key="dt_r")
    with col2:
        jaar = st.selectbox("Jaar", [2025, 2024], key="dt_j")

    swv_code = swv_df[swv_df['regio'] == regio]['swv_code'].values[0]
    filtered = dt_df[
        (dt_df['swv_code'] == swv_code) & (dt_df['jaar'] == jaar) & (dt_df['subgroep'] == 'Alle leerlingen')
    ]

    if not filtered.empty:
        row = filtered.iloc[0]
        st.divider()

        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            st.metric("VMBO-basis", f"{row['vmbo_b_pct']:.1f}%")
        with col2:
            st.metric("VMBO-kader", f"{row['vmbo_k_pct']:.1f}%")
        with col3:
            st.metric("VMBO-t", f"{row['vmbo_t_pct']:.1f}%")
        with col4:
            st.metric("HAVO", f"{row['havo_pct']:.1f}%")
        with col5:
            st.metric("VWO", f"{row['vwo_pct']:.1f}%")
        with col6:
            st.metric("Bijstelling", f"{row['bijstelling_omhoog_pct']:.1f}%",
                       help="% advies omhoog bijgesteld door doorstroomtoets")

        niveaus = ['VMBO-basis', 'VMBO-kader', 'VMBO-t', 'HAVO', 'VWO']
        waarden = [row['vmbo_b_pct'], row['vmbo_k_pct'], row['vmbo_t_pct'], row['havo_pct'], row['vwo_pct']]
        kleuren = [NL_RED, '#E8540A', NL_GREY, NL_ORANGE, NL_BLUE]

        fig = go.Figure(go.Bar(
            x=niveaus, y=waarden, marker_color=kleuren,
            text=[f"{v:.1f}%" for v in waarden], textposition='outside'
        ))
        fig.update_layout(
            title=f"Doorstroomtoets Adviesverdeling -- {regio} ({jaar})",
            yaxis_title="Percentage", height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    # Vergelijking alle regio's
    st.divider()
    st.subheader(f"Adviesverdeling Alle Regio's ({jaar})")
    alle = dt_df[(dt_df['jaar'] == jaar) & (dt_df['subgroep'] == 'Alle leerlingen')].copy()
    if not alle.empty:
        alle = alle.sort_values('vwo_pct', ascending=True)

        fig2 = go.Figure()
        for niveau, label, kleur in zip(
            ['vmbo_b_pct', 'vmbo_k_pct', 'vmbo_t_pct', 'havo_pct', 'vwo_pct'],
            ['VMBO-basis', 'VMBO-kader', 'VMBO-t', 'HAVO', 'VWO'],
            [NL_RED, '#E8540A', NL_GREY, NL_ORANGE, NL_BLUE]
        ):
            fig2.add_trace(go.Bar(
                y=alle['regio'], x=alle[niveau],
                name=label, marker_color=kleur, orientation='h'
            ))
        fig2.update_layout(
            barmode='stack', height=550,
            title=f"Doorstroomtoets Adviesverdeling per Regio ({jaar})",
            xaxis_title="Percentage"
        )
        st.plotly_chart(fig2, use_container_width=True)

    # Bijstellingen per regio
    st.subheader(f"Bijstellingen Omhoog per Regio ({jaar})")
    if not alle.empty:
        alle_sorted = alle.sort_values('bijstelling_omhoog_pct', ascending=True)
        fig3 = go.Figure(go.Bar(
            y=alle_sorted['regio'], x=alle_sorted['bijstelling_omhoog_pct'],
            orientation='h',
            marker_color=[NL_RED if b > 10 else NL_ORANGE for b in alle_sorted['bijstelling_omhoog_pct']],
            text=[f"{b:.1f}%" for b in alle_sorted['bijstelling_omhoog_pct']], textposition='outside'
        ))
        fig3.update_layout(
            title="Bijstelling Omhoog door Doorstroomtoets per Regio",
            xaxis_title="Bijstelling %", height=500
        )
        st.plotly_chart(fig3, use_container_width=True)


def render_export(ref_df, nk_df, dt_df, swv_df, landelijk_df):
    st.header("Exporteer Data")

    st.markdown("Download alle VERA-NL datasets als CSV-bestanden.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Samenwerkingsverbanden")
        st.dataframe(swv_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download SWV CSV", swv_df.to_csv(index=False),
            "vera_nl_swv.csv", "text/csv", use_container_width=True
        )
    with col2:
        st.subheader("Referentieniveau Data")
        st.dataframe(ref_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Referentieniveau CSV", ref_df.to_csv(index=False),
            "vera_nl_referentieniveau.csv", "text/csv", use_container_width=True
        )

    st.divider()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nieuwkomer Data")
        st.dataframe(nk_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Nieuwkomer CSV", nk_df.to_csv(index=False),
            "vera_nl_nieuwkomers.csv", "text/csv", use_container_width=True
        )
    with col2:
        st.subheader("Doorstroomtoets Data")
        st.dataframe(dt_df, use_container_width=True, hide_index=True)
        st.download_button(
            "Download Doorstroomtoets CSV", dt_df.to_csv(index=False),
            "vera_nl_doorstroomtoets.csv", "text/csv", use_container_width=True
        )

    st.divider()
    st.subheader("Landelijke Referentieniveaus")
    st.dataframe(landelijk_df, use_container_width=True, hide_index=True)
    st.download_button(
        "Download Landelijk CSV", landelijk_df.to_csv(index=False),
        "vera_nl_landelijk.csv", "text/csv", use_container_width=True
    )


# ============================================================================
# MAIN
# ============================================================================

def main():
    st.set_page_config(page_title="VERA-NL | Nederland Type 4 Detectie", page_icon="NL", layout="wide")

    st.markdown(f"""
    <style>
        .stApp {{ background-color: #fafafa; }}
        .block-container {{ padding-top: 2rem; }}
        h1, h2, h3 {{ color: {NL_BLUE}; }}
        .stButton > button {{ background-color: {NL_ORANGE}; color: white; }}
        .stButton > button:hover {{ background-color: #CC5200; color: white; }}
    </style>
    """, unsafe_allow_html=True)

    if not check_password():
        return

    swv_df = load_samenwerkingsverbanden()
    ref_df = load_referentieniveau_data(swv_df)
    nk_df = load_nieuwkomer_data(swv_df)
    dt_df = load_doorstroomtoets_data(swv_df)
    landelijk_df = load_landelijke_referentieniveaus()

    st.sidebar.markdown(f"""
    <div style="text-align: center; padding: 20px 0;">
        <h2 style="color: {NL_ORANGE}; margin: 0;">VERA-NL</h2>
        <p style="color: #666; font-size: 0.85rem; margin-top: 5px;">Nederland Implementatie</p>
    </div>
    """, unsafe_allow_html=True)
    st.sidebar.divider()

    page = st.sidebar.radio("Navigatie", [
        "Overzicht",
        "Referentieniveau Analyse",
        "NT2/Nieuwkomer Analyse",
        "Type 4 Detectie",
        "Prestatiekloof Analyse",
        "Doorstroomtoets Analyse",
        "Exporteer Data"
    ])

    st.sidebar.divider()
    st.sidebar.markdown(f"""
    **Databronnen:**
    - DUO open data (duo.nl)
    - Inspectie van het Onderwijs
    - CBS (Centraal Bureau voor de Statistiek)
    - LOWAN nieuwkomerdata

    **Type 4 Detectie:**
    - Mondeling vs Schriftelijk delta
    - Vlag-drempel: > 0.7 punten
    - Leraar-observatie + LVS-toetsen

    **Sleutelbegrippen:**
    - SWV: Samenwerkingsverband
    - BRIN: School-ID (4-char)
    - ISK: Internationale Schakelklas
    - NT2: Nederlands als Tweede Taal
    - LVS: Leerling Volg Systeem
    - 1F/1S: Referentieniveaus

    **Kerngegevens:**
    - ~2.6M leerlingen
    - ~30.000+ nieuwkomers
    - ~150 samenwerkingsverbanden
    - 15 pilot-regio's

    ---
    [H-EDU.Solutions](https://h-edu.solutions)
    """)

    if page == "Overzicht":
        render_overview(swv_df)
    elif page == "Referentieniveau Analyse":
        render_referentieniveau(ref_df, landelijk_df)
    elif page == "NT2/Nieuwkomer Analyse":
        render_nieuwkomer_analyse(nk_df, swv_df)
    elif page == "Type 4 Detectie":
        render_type4(ref_df, swv_df)
    elif page == "Prestatiekloof Analyse":
        render_achievement_gaps(dt_df, swv_df)
    elif page == "Doorstroomtoets Analyse":
        render_doorstroomtoets(dt_df, swv_df)
    elif page == "Exporteer Data":
        render_export(ref_df, nk_df, dt_df, swv_df, landelijk_df)


if __name__ == "__main__":
    main()
