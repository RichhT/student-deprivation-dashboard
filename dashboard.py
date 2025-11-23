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
    with open('anonymised_data.csv', 'r') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [col.replace('\xa0', ' ') for col in reader.fieldnames]
        data = list(reader)
    return data

data = load_data()
total_students = len(data)

# Header
st.title("📊 Student Deprivation Dashboard")
st.markdown("### Analysis of Disadvantage and Vulnerability Factors")
st.markdown("---")

# Sidebar filters
st.sidebar.header("Filters")
year_groups = sorted(set(row['NC Year(s) for this academic year'] for row in data))
selected_years = st.sidebar.multiselect(
    "Select Year Groups",
    year_groups,
    default=year_groups
)

# Filter data
filtered_data = [row for row in data if row['NC Year(s) for this academic year'] in selected_years]
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
        'Child Protection': cp,
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

# Key insights
st.markdown("---")
st.subheader("Key Insights")

col1, col2, col3 = st.columns(3)

with col1:
    st.info(f"""
    **Multiple Deprivation**

    {sum(1 for row in filtered_data if int(row['Disadvantaged Count']) >= 3)} students ({sum(1 for row in filtered_data if int(row['Disadvantaged Count']) >= 3)/filtered_total*100:.1f}%)
    face 3 or more disadvantage factors
    """)

with col2:
    st.warning(f"""
    **Child Protection**

    {cp} students on child protection plans
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
