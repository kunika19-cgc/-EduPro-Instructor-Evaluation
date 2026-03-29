import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# Load data (same as before)
@st.cache_data
def load_data():
    teachers_df = pd.read_excel('edupro_data.xlsx', sheet_name='Teachers')
    courses_df = pd.read_excel('edupro_data.xlsx', sheet_name='Courses')
    transactions_df = pd.read_excel('edupro_data.xlsx', sheet_name='Transactions')
    
    # Merge
    merged = pd.merge(transactions_df, courses_df, on='CourseID')
    merged = pd.merge(merged, teachers_df, on='TeacherID')
    merged = merged.drop_duplicates(subset=['CourseID', 'TeacherID'])
    return teachers_df, courses_df, transactions_df, merged

teachers_df, courses_df, transactions_df, merged = load_data()

# Dashboard title
st.title("📊 EduPro: Instructor & Course Quality Dashboard")
st.markdown("Evaluating teaching effectiveness and course quality")

# Sidebar filters
st.sidebar.header("Filters")
selected_expertise = st.sidebar.multiselect(
    "Select Expertise Areas",
    options=teachers_df['Expertise'].unique(),
    default=teachers_df['Expertise'].unique()
)

rating_range = st.sidebar.slider(
    "Teacher Rating Range",
    min_value=float(teachers_df['TeacherRating'].min()),
    max_value=float(teachers_df['TeacherRating'].max()),
    value=(3.0, 5.0)
)

# Filter data
filtered_teachers = teachers_df[
    (teachers_df['Expertise'].isin(selected_expertise)) &
    (teachers_df['TeacherRating'] >= rating_range[0]) &
    (teachers_df['TeacherRating'] <= rating_range[1])
]

# Tab layout
tab1, tab2, tab3, tab4 = st.tabs(["🏆 Instructor Leaderboard", "📈 Experience vs Rating", "🎯 Expertise Performance", "📊 Course Quality"])

with tab1:
    st.header("Top Performing Instructors")
    top_instructors = filtered_teachers.nlargest(10, 'TeacherRating')[['TeacherName', 'Expertise', 'YearsOfExperience', 'TeacherRating']]
    st.dataframe(top_instructors)
    
    # Bottom performers
    st.subheader("Instructors Needing Support")
    bottom_instructors = filtered_teachers.nsmallest(5, 'TeacherRating')[['TeacherName', 'Expertise', 'TeacherRating']]
    st.dataframe(bottom_instructors)

with tab2:
    st.header("Experience vs Performance")
    fig = px.scatter(filtered_teachers, x='YearsOfExperience', y='TeacherRating', 
                     color='Expertise', size='Age', 
                     title="Years of Experience vs Teacher Rating",
                     labels={'YearsOfExperience': 'Years of Experience', 'TeacherRating': 'Teacher Rating'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Correlation
    corr = filtered_teachers['YearsOfExperience'].corr(filtered_teachers['TeacherRating'])
    st.metric("Correlation Coefficient", f"{corr:.3f}")

with tab3:
    st.header("Expertise Area Performance")
    expertise_rating = merged.groupby('Expertise')['CourseRating'].mean().sort_values(ascending=False).reset_index()
    fig = px.bar(expertise_rating, x='Expertise', y='CourseRating', 
                 title="Average Course Rating by Instructor Expertise",
                 color='CourseRating', color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    # Expertise with most consistent quality
    expertise_std = merged.groupby('Expertise')['CourseRating'].std().reset_index()
    fig2 = px.bar(expertise_std, x='Expertise', y='CourseRating', 
                  title="Rating Consistency (Lower = More Consistent)",
                  color='CourseRating', color_continuous_scale='RdBu')
    st.plotly_chart(fig2, use_container_width=True)

with tab4:
    st.header("Course Quality Analysis")
    
    # Course rating by category and level
    course_quality = merged.groupby(['CourseCategory', 'CourseLevel'])['CourseRating'].mean().reset_index()
    fig = px.bar(course_quality, x='CourseCategory', y='CourseRating', color='CourseLevel',
                 title="Course Ratings by Category and Level", barmode='group')
    st.plotly_chart(fig, use_container_width=True)
    
    # Rating distribution
    fig2 = px.histogram(merged, x='CourseRating', nbins=20, 
                        title="Distribution of Course Ratings",
                        color='CourseLevel')
    st.plotly_chart(fig2, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("**EduPro Quality Evaluation Framework** | Data-driven insights for teaching excellence")