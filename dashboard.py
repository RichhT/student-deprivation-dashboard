import streamlit as st
import csv
from collections import Counter, defaultdict
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="Student Deprivation Dashboard",
    page_icon="📊",
    layout="wide"
)

# Load data
@st.cache_data
def load_data():
    with open('test_data.csv', 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [col.replace('\xa0', ' ') for col in reader.fieldnames]
        data = list(reader)
    return data

data = load_data()
total_students = len(data)

# Header
st.title("📊 Student Deprivation Dashboard")
st.markdown("### Analysis of Disadvantage and Vulnerability Factors")

# Create tabs
tab1, tab2 = st.tabs(["📊 Overview", "📈 Attendance & Suspensions by Disadvantage Type"])

st.sidebar.header("Filters")

# Function to categorize students by provision
def get_provision_type(row):
    reg_form = row['Registration form(s) this academic year']
    if 'LST' in reg_form:
        return 'Eduk8'
    elif 'AME' in reg_form:
        return 'Beacon'
    elif 'KJO' in reg_form:
        return 'R-Bridge'
    else:
        return 'Mainstream'

# Add provision type to each row
for row in data:
    row['Provision'] = get_provision_type(row)

# Provision filter
provision_types = ['Mainstream', 'Eduk8', 'Beacon', 'R-Bridge']
selected_provisions = st.sidebar.multiselect(
    "Select Provision Type",
    provision_types,
    default=provision_types
)

# Year group filter
year_groups = sorted(set(row['NC Year(s) for this academic year'] for row in data))
selected_years = st.sidebar.multiselect(
    "Select Year Groups",
    year_groups,
    default=year_groups
)

# Filter data
filtered_data = [row for row in data
                 if row['NC Year(s) for this academic year'] in selected_years
                 and row['Provision'] in selected_provisions]
filtered_total = len(filtered_data)

# Calculate metrics
disadvantaged = sum(1 for row in filtered_data if row['Disadvantaged?'] == 'Y')
disadvantaged_pct = (disadvantaged / filtered_total * 100) if filtered_total > 0 else 0

fsm = sum(1 for row in filtered_data if row['Ever 6 FSM at any time between 01 Aug 2020 and 30 Aug 2026?'] == 'Yes')
fsm_pct = (fsm / filtered_total * 100) if filtered_total > 0 else 0

pp_recipient = sum(1 for row in filtered_data if row['Pupil Premium Recipient at any time between 01 Aug 2020 and 30 Aug 2026?'] == 'Yes')
pp_pct = (pp_recipient / filtered_total * 100) if filtered_total > 0 else 0

sen = sum(1 for row in filtered_data if row['SEN at any time this academic year?'] == 'Yes')
sen_pct = (sen / filtered_total * 100) if filtered_total > 0 else 0

young_carer = sum(1 for row in filtered_data if row['Young Carer at any time this academic year?'] == 'Yes')
lac = sum(1 for row in filtered_data if row['Looked After (In Care) Status'].strip())
cp = sum(1 for row in filtered_data if row['Child Protection Status'].strip())
l3 = sum(1 for row in filtered_data if row['L3 Graduated Response Recipient'] == 'Yes')

# Tab 1: Overview
with tab1:
    st.markdown("---")

    # Top metrics
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Students", filtered_total)

    with col2:
        st.metric("Disadvantaged", f"{disadvantaged_pct:.1f}%", f"{disadvantaged} students")

    with col3:
        st.metric("Ever 6 FSM", f"{fsm_pct:.1f}%", f"{fsm} students")

    with col4:
        st.metric("SEN", f"{sen_pct:.1f}%", f"{sen} students")

    with col5:
        st.metric("Pupil Premium", f"{pp_pct:.1f}%", f"{pp_recipient} students")

    st.markdown("---")

    # Provision breakdown summary
    if len(selected_provisions) > 1:
        st.subheader("Students by Provision Type")

        provision_counts = {}
        provision_disadvantaged = {}

        for prov in provision_types:
            prov_students = [row for row in filtered_data if row['Provision'] == prov]
            provision_counts[prov] = len(prov_students)
            provision_disadvantaged[prov] = sum(1 for row in prov_students if row['Disadvantaged?'] == 'Y')

        col1, col2, col3, col4 = st.columns(4)

        for i, (prov, col) in enumerate(zip(provision_types, [col1, col2, col3, col4])):
            with col:
                count = provision_counts[prov]
                dis = provision_disadvantaged[prov]
                dis_pct = (dis / count * 100) if count > 0 else 0
                st.metric(prov, count, f"{dis_pct:.1f}% disadvantaged")

        st.markdown("---")

    # Row 1: Overview charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Overall Deprivation Status")

        dep_counts = Counter(row['Disadvantaged?'] for row in filtered_data)
        disadvantaged_count = dep_counts.get('Y', 0)
        not_disadvantaged_count = filtered_total - disadvantaged_count

        fig = go.Figure(data=[go.Pie(
            labels=['Disadvantaged', 'Not Disadvantaged'],
            values=[disadvantaged_count, not_disadvantaged_count],
            hole=0.4,
            marker_colors=['#e74c3c', '#2ecc71']
        )])
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Number of Disadvantage Factors")

        dis_count = Counter(int(row['Disadvantaged Count']) for row in filtered_data)

        fig = go.Figure(data=[go.Bar(
            x=list(sorted(dis_count.keys())),
            y=[dis_count[k] for k in sorted(dis_count.keys())],
            marker_color='#3498db',
            text=[dis_count[k] for k in sorted(dis_count.keys())],
            textposition='auto'
        )])
        fig.update_layout(
            xaxis_title="Number of Factors",
            yaxis_title="Number of Students",
            height=350
        )
        st.plotly_chart(fig, use_container_width=True)

    # Row 2: Deprivation by year group
    st.subheader("Deprivation by Year Group")

    year_dis = defaultdict(lambda: {'total': 0, 'disadvantaged': 0})
    for row in filtered_data:
        year = row['NC Year(s) for this academic year']
        year_dis[year]['total'] += 1
        if row['Disadvantaged?'] == 'Y':
            year_dis[year]['disadvantaged'] += 1

    years = sorted(year_dis.keys())
    percentages = [(year_dis[y]['disadvantaged']/year_dis[y]['total']*100) if year_dis[y]['total'] > 0 else 0 for y in years]
    counts = [year_dis[y]['disadvantaged'] for y in years]
    totals = [year_dis[y]['total'] for y in years]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=years,
        y=percentages,
        marker_color='#e67e22',
        text=[f"{counts[i]}/{totals[i]}<br>({percentages[i]:.1f}%)" for i in range(len(years))],
        textposition='auto',
    ))
    fig.update_layout(
        xaxis_title="Year Group",
        yaxis_title="Percentage Disadvantaged (%)",
        height=400,
        yaxis_range=[0, 100]
    )
    st.plotly_chart(fig, use_container_width=True)

    # Row 3: Vulnerability factors
    st.subheader("Vulnerability Factors Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        vulnerability_data = {
            'SEN': sen,
            'Ever 6 FSM': fsm,
            'Pupil Premium': pp_recipient,
            'CS Involvement': cp,
            'L3 Response': l3,
            'Young Carers': young_carer,
            'Looked After': lac
        }

        fig = go.Figure(data=[go.Bar(
            y=list(vulnerability_data.keys()),
            x=list(vulnerability_data.values()),
            orientation='h',
            marker_color='#9b59b6',
            text=list(vulnerability_data.values()),
            textposition='auto'
        )])
        fig.update_layout(
            xaxis_title="Number of Students",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        vulnerability_pct = {
            k: (v / filtered_total * 100) if filtered_total > 0 else 0
            for k, v in vulnerability_data.items()
        }

        fig = go.Figure(data=[go.Bar(
            y=list(vulnerability_pct.keys()),
            x=list(vulnerability_pct.values()),
            orientation='h',
            marker_color='#1abc9c',
            text=[f"{v:.1f}%" for v in vulnerability_pct.values()],
            textposition='auto'
        )])
        fig.update_layout(
            xaxis_title="Percentage of Students (%)",
            height=400,
            xaxis_range=[0, max(vulnerability_pct.values()) * 1.1]
        )
        st.plotly_chart(fig, use_container_width=True)

    # Row 4: National Comparison
    st.markdown("---")
    st.subheader("Comparison with National Averages")

    # National averages from official sources
    national_data = {
        'SEN': {'school': sen_pct, 'national': 17.3, 'source': 'DfE Statistics: SEN in England 2024'},
        'Ever 6 FSM': {'school': fsm_pct, 'national': 25.0, 'source': 'DfE Statistics: Schools, Pupils and Their Characteristics 2024'},
        'Pupil Premium': {'school': pp_pct, 'national': 23.7, 'source': 'DfE Statistics: Pupil Premium Allocations 2024/25'},
        'Looked After': {'school': (lac/filtered_total*100) if filtered_total > 0 else 0, 'national': 0.9, 'source': 'DfE Statistics: Children Looked After in England 2024'}
    }

    categories = list(national_data.keys())
    school_values = [national_data[cat]['school'] for cat in categories]
    national_values = [national_data[cat]['national'] for cat in categories]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='Our School',
        x=categories,
        y=school_values,
        marker_color='#e74c3c',
        text=[f"{v:.1f}%" for v in school_values],
        textposition='auto'
    ))
    fig.add_trace(go.Bar(
        name='National Average',
        x=categories,
        y=national_values,
        marker_color='#3498db',
        text=[f"{v:.1f}%" for v in national_values],
        textposition='auto'
    ))

    fig.update_layout(
        barmode='group',
        xaxis_title="Indicator",
        yaxis_title="Percentage (%)",
        height=400,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    st.plotly_chart(fig, use_container_width=True)

    # Sources
    with st.expander("📚 Data Sources"):
        st.markdown("**National comparison data sources:**")
        for cat, info in national_data.items():
            st.markdown(f"- **{cat}**: {info['source']}")
        st.markdown("\n**Links:**")
        st.markdown("- [Department for Education Statistics](https://explore-education-statistics.service.gov.uk/)")
        st.markdown("- [Special Educational Needs in England](https://explore-education-statistics.service.gov.uk/find-statistics/special-educational-needs-in-england)")
        st.markdown("- [Schools, Pupils and Their Characteristics](https://explore-education-statistics.service.gov.uk/find-statistics/school-pupils-and-their-characteristics)")
        st.markdown("- [Children Looked After in England](https://explore-education-statistics.service.gov.uk/find-statistics/children-looked-after-in-england-including-adoptions)")

    # Row 4b: Overlapping Disadvantages Comparison
    st.markdown("---")
    st.subheader("Overlapping Disadvantages: Our School vs National")

    st.markdown("""
    While comprehensive multi-factor disadvantage data isn't published nationally, the DfE does track some **two-way overlaps**.
    These show how disadvantage factors cluster together:
    """)

    # Calculate our school's overlaps
    sen_fsm_overlap = sum(1 for row in filtered_data if row['SEN at any time this academic year?'] == 'Yes'
                           and row['Ever 6 FSM at any time between 01 Aug 2020 and 30 Aug 2026?'] == 'Yes')
    sen_total = sum(1 for row in filtered_data if row['SEN at any time this academic year?'] == 'Yes')
    sen_fsm_pct = (sen_fsm_overlap / sen_total * 100) if sen_total > 0 else 0

    cp_fsm_overlap = sum(1 for row in filtered_data if row['Child Protection Status'].strip()
                          and row['Ever 6 FSM at any time between 01 Aug 2020 and 30 Aug 2026?'] == 'Yes')
    cp_total = sum(1 for row in filtered_data if row['Child Protection Status'].strip())
    cp_fsm_pct = (cp_fsm_overlap / cp_total * 100) if cp_total > 0 else 0

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### SEN Pupils Eligible for FSM")

        overlap_data = {
            'Category': ['Our School\n(SEN + FSM)', 'National Average\n(SEN + FSM)'],
            'Percentage': [sen_fsm_pct, 40.8],  # National average of EHC (43.8%) and SEN Support (39.3%)
            'Description': [
                f'{sen_fsm_overlap}/{sen_total} SEN pupils',
                'Avg of EHC plans (43.8%) & SEN Support (39.3%)'
            ]
        }

        fig = go.Figure(data=[go.Bar(
            x=overlap_data['Category'],
            y=overlap_data['Percentage'],
            marker_color=['#e74c3c', '#3498db'],
            text=[f"{v:.1f}%<br>{overlap_data['Description'][i]}" for i, v in enumerate(overlap_data['Percentage'])],
            textposition='auto',
        )])

        fig.update_layout(
            yaxis_title="% of SEN Pupils who are FSM-Eligible",
            height=400,
            yaxis_range=[0, 100],
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### CS Involvement Cases Eligible for FSM")

        # For CS involvement, use national Child Protection Plan data
        overlap_data_cp = {
            'Category': ['Our School\n(CS + FSM)', 'National Average\n(CPP + FSM)'],
            'Percentage': [cp_fsm_pct, 78.1],  # National: 78.1% of children on CP plans are FSM-eligible
            'Description': [
                f'{cp_fsm_overlap}/{cp_total} CS cases',
                'Children on CP Plans'
            ]
        }

        fig = go.Figure(data=[go.Bar(
            x=overlap_data_cp['Category'],
            y=overlap_data_cp['Percentage'],
            marker_color=['#e74c3c', '#3498db'],
            text=[f"{v:.1f}%<br>{overlap_data_cp['Description'][i]}" for i, v in enumerate(overlap_data_cp['Percentage'])],
            textposition='auto',
        )])

        fig.update_layout(
            yaxis_title="% of CS Cases who are FSM-Eligible",
            height=400,
            yaxis_range=[0, 100],
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.info("""
    **Key Insight:** These overlaps show how disadvantage factors cluster together. Nationally, pupils with one form of disadvantage
    (like SEN or CS involvement) are **2-3x more likely** to also experience economic disadvantage (FSM). Our school's overlap patterns
    help identify students facing multiple, compounding challenges.
    """)

    # Sources for overlap data
    with st.expander("📚 Overlap Data Sources"):
        st.markdown("**National overlap data sources:**")
        st.markdown("- **SEN + FSM overlap**: DfE Special Educational Needs in England 2024/25")
        st.markdown("- **CS Involvement + FSM overlap**: DfE Outcomes for Children in Need, including children looked after 2023/24")
        st.markdown("\n**Links:**")
        st.markdown("- [Special Educational Needs in England](https://explore-education-statistics.service.gov.uk/find-statistics/special-educational-needs-in-england)")
        st.markdown("- [Outcomes for Children in Need](https://explore-education-statistics.service.gov.uk/find-statistics/outcomes-for-children-in-need-including-children-looked-after-by-local-authorities-in-england)")

    # Row 5: Pyramid Visualization
    st.markdown("---")
    st.subheader("Disadvantage Markers Pyramid")

    dis_count = Counter(int(row['Disadvantaged Count']) for row in filtered_data)
    max_markers = max(dis_count.keys()) if dis_count else 0

    # Create pyramid data (reversed for visual effect)
    pyramid_levels = []
    for i in range(max_markers, -1, -1):
        count = dis_count.get(i, 0)
        pct = (count / filtered_total * 100) if filtered_total > 0 else 0
        pyramid_levels.append({
            'level': i,
            'count': count,
            'percentage': pct,
            'label': f"{i} marker{'s' if i != 1 else ''}"
        })

    # Create color scale - darker red for more markers
    colors = ['#27ae60', '#f39c12', '#e67e22', '#e74c3c', '#c0392b', '#8e44ad', '#6c3483']
    marker_colors = [colors[min(level['level'], len(colors)-1)] for level in pyramid_levels]

    fig = go.Figure()

    # Create horizontal bar chart (pyramid style)
    fig.add_trace(go.Bar(
        x=[level['count'] for level in pyramid_levels],
        y=[level['label'] for level in pyramid_levels],
        orientation='h',
        marker=dict(
            color=marker_colors,
            line=dict(color='white', width=2)
        ),
        text=[f"{level['count']} students ({level['percentage']:.1f}%)" for level in pyramid_levels],
        textposition='auto',
        hovertemplate='<b>%{y}</b><br>Students: %{x}<br>Percentage: %{text}<extra></extra>'
    ))

    fig.update_layout(
        xaxis_title="Number of Students",
        yaxis_title="Disadvantage Markers",
        height=450,
        showlegend=False,
        yaxis=dict(autorange="reversed")  # This makes it pyramid-like with 0 at bottom
    )

    st.plotly_chart(fig, use_container_width=True)

    st.markdown("""
    **Understanding the Pyramid:**
    - Students at the **bottom** (0 markers) have no identified disadvantage factors
    - Students at the **top** face multiple, compounding disadvantages
    - The **color intensity** increases with the number of markers (darker = more disadvantaged)
    """)

    # Row 6: Detailed breakdown by year and factor
    st.markdown("---")
    st.subheader("Detailed Analysis by Year Group")

    # Create a heatmap
    factors = ['Disadvantaged?', 'SEN at any time this academic year?',
               'Ever 6 FSM at any time between 01 Aug 2020 and 30 Aug 2026?',
               'Pupil Premium Recipient at any time between 01 Aug 2020 and 30 Aug 2026?',
               'Young Carer at any time this academic year?']
    factor_labels = ['Disadvantaged', 'SEN', 'FSM', 'Pupil Premium', 'Young Carer']

    heatmap_data = []
    for year in sorted(year_dis.keys()):
        year_data = [row for row in filtered_data if row['NC Year(s) for this academic year'] == year]
        year_total = len(year_data)

        row_values = []
        for factor in factors:
            if factor == 'Disadvantaged?':
                count = sum(1 for row in year_data if row[factor] == 'Y')
            else:
                count = sum(1 for row in year_data if row[factor] == 'Yes')
            pct = (count / year_total * 100) if year_total > 0 else 0
            row_values.append(pct)
        heatmap_data.append(row_values)

    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=factor_labels,
        y=sorted(year_dis.keys()),
        colorscale='RdYlGn_r',
        text=[[f"{val:.1f}%" for val in row] for row in heatmap_data],
        texttemplate="%{text}",
        textfont={"size": 12},
        colorbar=dict(title="Percentage")
    ))
    fig.update_layout(
        xaxis_title="Factor",
        yaxis_title="Year Group",
        height=400
    )
    st.plotly_chart(fig, use_container_width=True)

    # Row 7: Outcomes by Disadvantage Level
    st.markdown("---")
    st.subheader("Outcomes by Number of Disadvantage Markers")

    st.markdown("""
    This section shows how student outcomes vary based on the number of disadvantage markers they have.
    Understanding these patterns helps target interventions effectively.
    """)

    # Calculate outcomes by disadvantage count
    outcomes_by_count = defaultdict(lambda: {
        'attendance': [],
        'suspensions': [],
        'atl_scores': [],
        'hw_scores': []
    })

    # ATL and Homework value mapping
    score_map = {'Outstanding': 4, 'Good': 3, 'Requires Improvement': 2, 'Inadequate': 1}

    for row in filtered_data:
        dis_count = int(row.get('Disadvantaged Count', 0))

        # Attendance
        attendance_str = row.get('Statutory/Roll Call Attendance (Present) this academic year', '').strip().replace('%', '')
        if attendance_str:
            try:
                outcomes_by_count[dis_count]['attendance'].append(float(attendance_str))
            except:
                pass

        # Suspensions
        susp_str = row.get('Suspensions between 02 Aug 2021 and 30 Aug 2026', '').strip()
        if susp_str:
            try:
                outcomes_by_count[dis_count]['suspensions'].append(int(susp_str))
            except:
                pass

        # ATL - calculate average across all subjects where data exists
        atl_cols = [col for col in row.keys() if col.startswith('ATL:')]
        atl_values = []
        for col in atl_cols:
            val = row.get(col, '').strip()
            if val in score_map:
                atl_values.append(score_map[val])
        if atl_values:
            outcomes_by_count[dis_count]['atl_scores'].append(sum(atl_values) / len(atl_values))

        # Homework - calculate average across all subjects where data exists
        hw_cols = [col for col in row.keys() if col.startswith('Homework:')]
        hw_values = []
        for col in hw_cols:
            val = row.get(col, '').strip()
            if val in score_map:
                hw_values.append(score_map[val])
        if hw_values:
            outcomes_by_count[dis_count]['hw_scores'].append(sum(hw_values) / len(hw_values))

    # Calculate averages
    counts = sorted(outcomes_by_count.keys())
    avg_attendance = []
    avg_suspensions = []
    avg_atl = []
    avg_hw = []
    student_counts = []

    for count in counts:
        data = outcomes_by_count[count]
        student_counts.append(len([row for row in filtered_data if int(row.get('Disadvantaged Count', 0)) == count]))

        avg_attendance.append(sum(data['attendance']) / len(data['attendance']) if data['attendance'] else None)
        avg_suspensions.append(sum(data['suspensions']) / len(data['suspensions']) if data['suspensions'] else None)
        avg_atl.append(sum(data['atl_scores']) / len(data['atl_scores']) if data['atl_scores'] else None)
        avg_hw.append(sum(data['hw_scores']) / len(data['hw_scores']) if data['hw_scores'] else None)

    # Create visualizations
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Average Attendance by Disadvantage Markers")

        fig = go.Figure()
        valid_attendance = [(c, a, n) for c, a, n in zip(counts, avg_attendance, student_counts) if a is not None]
        if valid_attendance:
            c_vals, a_vals, n_vals = zip(*valid_attendance)
            fig.add_trace(go.Bar(
                x=[f"{c} markers" for c in c_vals],
                y=a_vals,
                marker_color='#3498db',
                text=[f"{a:.1f}%<br>n={n}" for a, n in zip(a_vals, n_vals)],
                textposition='auto'
            ))
            fig.update_layout(
                yaxis_title="Average Attendance (%)",
                height=400,
                yaxis_range=[0, 100]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No attendance data available for filtered students")

    with col2:
        st.markdown("#### Average Suspensions by Disadvantage Markers")

        fig = go.Figure()
        valid_suspensions = [(c, s, n) for c, s, n in zip(counts, avg_suspensions, student_counts) if s is not None]
        if valid_suspensions:
            c_vals, s_vals, n_vals = zip(*valid_suspensions)
            fig.add_trace(go.Bar(
                x=[f"{c} markers" for c in c_vals],
                y=s_vals,
                marker_color='#e74c3c',
                text=[f"{s:.2f}<br>n={n}" for s, n in zip(s_vals, n_vals)],
                textposition='auto'
            ))
            fig.update_layout(
                yaxis_title="Average Number of Suspensions",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No suspension data available for filtered students")

    st.info("""
    **Understanding the Outcomes:** These visualizations show how attendance and suspensions vary by disadvantage level.
    The 'n=' values show the number of students with data available for each marker count.
    """)

    # Key insights
    st.markdown("---")
    st.subheader("Key Insights")

    col1, col2, col3 = st.columns(3)

    with col1:
        multi_dep_count = sum(1 for row in filtered_data if int(row.get('Disadvantaged Count', 0)) >= 3)
        multi_dep_pct = (multi_dep_count / filtered_total * 100) if filtered_total > 0 else 0
        st.info(f"""
        **Multiple Deprivation**

        {multi_dep_count} students ({multi_dep_pct:.1f}%)
        face 3 or more disadvantage factors
        """)

    with col2:
        st.warning(f"""
        **CS Involvement**

        {cp} students with children's services involvement
        requiring urgent support and monitoring
        """)

    with col3:
        st.error(f"""
        **Looked After Children**

        {lac} students in care requiring
        specialist provision and support
        """)

        # Footer
        st.markdown("---")
        st.caption("Data source: Anonymised school demographic data")

# Tab 2: Attendance & Suspensions by Disadvantage Type
with tab2:
    st.markdown("---")
    st.subheader("Filter by Disadvantage Type")

    st.markdown("""
    Select specific types of disadvantage to analyze attendance and suspension patterns.
    You can select multiple types to see overlapping groups.
    """)

    # Disadvantage type filters
    col1, col2, col3 = st.columns(3)

    with col1:
        filter_ap = st.checkbox("AP Provision (LST/KJO/AME)", value=False)
        filter_yc = st.checkbox("Young Carers", value=False)
        filter_sen = st.checkbox("SEN", value=False)

    with col2:
        filter_fsm = st.checkbox("Ever 6 FSM", value=False)
        filter_plac = st.checkbox("PLAC", value=False)
        filter_lac = st.checkbox("Looked After", value=False)

    with col3:
        filter_cp = st.checkbox("CS Involvement", value=False)
        filter_l3 = st.checkbox("L3 Response", value=False)

    # Filter data based on selections
    import re

    def matches_filters(row):
        if not any([filter_ap, filter_yc, filter_sen, filter_fsm, filter_plac, filter_lac, filter_cp, filter_l3]):
            return True  # If no filters selected, show all

        matches = []
        if filter_ap:
            matches.append(bool(re.search(r'(LST|KJO|AME)', row.get('Registration form(s) this academic year', ''))))
        if filter_yc:
            matches.append(row.get('Young Carer at any time this academic year?', '') == 'Yes')
        if filter_sen:
            matches.append(row.get('SEN at any time this academic year?', '') == 'Yes')
        if filter_fsm:
            matches.append(row.get('Ever 6 FSM at any time between 01 Aug 2020 and 30 Aug 2026?', '') == 'Yes')
        if filter_plac:
            matches.append(row.get('PLAC', '') == 'Yes')
        if filter_lac:
            matches.append(bool(row.get('Looked After (In Care) Status', '').strip()))
        if filter_cp:
            matches.append(bool(row.get('Child Protection Status', '').strip()))
        if filter_l3:
            matches.append(bool(row.get('L3 Graduated Response Recipient', '').strip()))

        return all(matches)  # All selected filters must match

    tab2_filtered = [row for row in filtered_data if matches_filters(row)]
    tab2_total = len(tab2_filtered)

    st.info(f"**{tab2_total} students** match the selected disadvantage criteria (from {filtered_total} students matching provision/year filters)")

    if tab2_total > 0:
        st.markdown("---")

        # Attendance Analysis
        st.subheader("Attendance Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Average Attendance")

            # Calculate average attendance
            attendance_values = []
            for row in tab2_filtered:
                att_str = row.get('Statutory/Roll Call Attendance (Present) this academic year', '').strip().replace('%', '')
                if att_str:
                    try:
                        attendance_values.append(float(att_str))
                    except:
                        pass

            if attendance_values:
                avg_att = sum(attendance_values) / len(attendance_values)
                st.metric("Average Attendance", f"{avg_att:.1f}%", f"n={len(attendance_values)}")

                # Distribution stats
                st.markdown(f"""
                - **Minimum**: {min(attendance_values):.1f}%
                - **Maximum**: {max(attendance_values):.1f}%
                - **Median**: {sorted(attendance_values)[len(attendance_values)//2]:.1f}%
                """)
            else:
                st.info("No attendance data available for selected students")

        with col2:
            st.markdown("#### Attendance Distribution (10% Bands)")

            if attendance_values:
                # Create 10% bands
                bands = ['0-10%', '10-20%', '20-30%', '30-40%', '40-50%',
                        '50-60%', '60-70%', '70-80%', '80-90%', '90-100%']
                band_counts = [0] * 10

                for att in attendance_values:
                    band_idx = min(int(att // 10), 9)
                    band_counts[band_idx] += 1

                fig = go.Figure(data=[go.Bar(
                    x=bands,
                    y=band_counts,
                    marker_color='#3498db',
                    text=band_counts,
                    textposition='auto'
                )])

                fig.update_layout(
                    xaxis_title="Attendance Band",
                    yaxis_title="Number of Students",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No attendance data available")

        # Suspensions Analysis
        st.markdown("---")
        st.subheader("Suspensions Analysis")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Suspension Statistics")

            # Calculate suspension stats
            suspension_values = []
            for row in tab2_filtered:
                susp_str = row.get('Suspensions between 02 Aug 2021 and 30 Aug 2026', '').strip()
                if susp_str:
                    try:
                        suspension_values.append(int(susp_str))
                    except:
                        pass

            if suspension_values:
                total_susp = sum(suspension_values)
                avg_susp = total_susp / len(suspension_values)
                students_with_susp = sum(1 for s in suspension_values if s > 0)

                st.metric("Total Suspensions", total_susp)
                st.metric("Average per Student", f"{avg_susp:.2f}", f"n={len(suspension_values)}")
                st.metric("Students with Suspensions", f"{students_with_susp} ({students_with_susp/len(suspension_values)*100:.1f}%)")
            else:
                st.info("No suspension data available for selected students")

        with col2:
            st.markdown("#### Suspensions Distribution")

            if suspension_values:
                # Count students by suspension count
                from collections import Counter
                susp_counts = Counter(suspension_values)

                # Get suspension levels
                max_susp = max(suspension_values)
                susp_levels = list(range(min(10, max_susp + 1)))  # Show 0-9 or up to max
                if max_susp >= 10:
                    susp_levels.append(f"10+")

                level_counts = []
                for level in susp_levels:
                    if level == "10+":
                        level_counts.append(sum(count for susp, count in susp_counts.items() if susp >= 10))
                    else:
                        level_counts.append(susp_counts.get(level, 0))

                fig = go.Figure(data=[go.Bar(
                    x=[str(l) for l in susp_levels],
                    y=level_counts,
                    marker_color='#e74c3c',
                    text=level_counts,
                    textposition='auto'
                )])

                fig.update_layout(
                    xaxis_title="Number of Suspensions",
                    yaxis_title="Number of Students",
                    height=400
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No suspension data available")
    else:
        st.warning("No students match the selected disadvantage criteria. Please adjust your filters.")
