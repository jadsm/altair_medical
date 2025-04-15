import altair as alt
import pandas as pd

def plot_timeline(df,timevar='months',colorvar='devices',shapevar='measurement',groupvar='Group',shapevarrange=["first", "last",'withdrawn','deceased','diagnosis']):
    palette = {"Diseased":"#1E88E5","Healthy":"#004D40"}

    base = alt.Chart(df).encode(
        alt.X(f"{timevar}:Q").title(f"{timevar} from consent"),
        alt.Y("patient:N",sort = 'ascending')                                
            .axis(offset=0, ticks=False,labels=False, minExtent=0, domain=False)
            .title("Participant")
    )

    line_first = base.mark_line().encode(
        detail="patient:N",
        opacity=alt.value(.8),
        color=alt.Color(f"{colorvar}:N").scale(range=['#2C75FF','black','red']),
    ).transform_filter(alt.FieldOneOfPredicate(field=shapevar, oneOf=shapevarrange[:-1]))

    point_base = base.mark_point(filled=True).encode(
        opacity=alt.value(1),
        shape = alt.Shape(shapevar).scale(domain=["first", "last",'withdrawn','deceased','diagnosis'],
                                               range=['triangle-left', 'triangle-right','triangle', 'cross','circle']).title('timepoint'),
        ).transform_filter(alt.FieldOneOfPredicate(field="measurement", 
                                                    oneOf=shapevarrange))
    

    point = point_base.encode(color=alt.Color(groupvar,sort = alt.SortField('Group_order')).scale(domain=list(palette.keys()),range=list(palette.values())),
        size=alt.condition(f"datum['{shapevar}'] == 'first' || datum['{shapevar}'] == 'last'",
        alt.value(50),  
        alt.value(100)   
    ))
    
    reference_line= alt.Chart(pd.DataFrame({'x':[0]})).mark_rule(color='black', size=1).encode(x='x')    
    chart = (line_first + point + reference_line).resolve_scale(color='independent').properties(
                width=800,
                height=250
            ).configure_axis(labelFontSize=20,titleFontSize=22
            ).configure_title(fontSize=20, 
            anchor="middle").configure_legend(titleColor='black', 
            titleFontSize=20,labelFontSize=20).interactive()
    return chart

def plot_kaplanmeier(df_plot,colour,palette,ci=True,title='Survival'):
    base = alt.Chart(df_plot)
    
    line = (
    base
    .mark_line(interpolate='step-after')
    .encode(
            x=alt.X("timeline", axis=alt.Axis(title="Days from randomization")),
            y=alt.Y("KM_estimate", axis=alt.Axis(title="Survival probability")),
            color = alt.Color(colour).scale(range=palette),
            size=alt.value(3)
    )
    )

    dots = (
    base
    .mark_circle(filled=True,interpolate='step-after')
    .encode(
            x=alt.X("timeline", axis=alt.Axis(title="Days from randomization")),
            y=alt.Y("KM_estimate", axis=alt.Axis(title="Survival probability")),
            color = alt.Color(colour).scale(range=palette),
            tooltip = ["timeline","KM_estimate"],
            size=alt.value(30)
    )
    )

    if ci:
            band = line.mark_area(opacity=0.4, interpolate='step-after').encode(
            x='timeline',
            y='lower_bound',
            y2='upper_bound',
            color = alt.Color(colour).scale(range=palette)
            )

            fig = line + band + dots
    else:
            fig = line + dots

    fig = fig.properties(
            width=800,
            height=850,title=title
        )
    return fig

def plot_swimmer(df,title,legend=True,colors_outcome=['green','orange','orange','red','red','gray','gray']):
        
    base = alt.Chart(df).transform_calculate(
    order='datum.treatment_classification_num'
    ).encode(
    alt.X(f"days_from_treatment:Q").title("days from treatment start"),
    alt.Y("Participant:N",sort = alt.SortField('order')
            )
            .axis(offset=0, ticks=False, minExtent=0, domain=False).title('patient ID')
    )

    palette = ["#138086",'#DC8665'] if df.query('event_type == "drug"')['event_outcome'].nunique()==2 else ['#DC8665']
    colourset = alt.Color('event_outcome').scale(range=palette).legend(title='Treatment',orient='bottom') if legend else alt.Color('event_outcome').scale(range=palette).legend(None)
    
    line0 = base.mark_line().encode(
    detail="Participant",
    color=colourset,
    opacity=alt.value(.7),
    yOffset=alt.value(15),
    size = alt.value(7)
).transform_filter(alt.FieldEqualPredicate(field='event_type', equal='drug'))
    
    colourset = alt.Color('event_outcome').scale(range=colors_outcome).legend(title='Outcome',orient='bottom') if legend else alt.Color('event_outcome').scale(range=colors_outcome).legend(None)
    line = base.mark_line().encode(
    detail="Participant",
    size=alt.value(17),
    color=colourset,
    opacity=alt.value(.6),
    ).transform_filter(alt.FieldEqualPredicate(field='event_type', equal='scan'))

    point = base.mark_point(filled=False).encode(
    color=alt.value("black"),
    size=alt.value(100),
    opacity=alt.value(.8),
    shape = alt.Shape('event_type').legend(title='Events',orient='bottom'),
    tooltip=['Treatment_arm', 'Participant',  'days_from_treatment','days_from_randomization', 'event_grade',
    'event_outcome', 'event_type']).transform_filter(alt.FieldOneOfPredicate(field='event_type', oneOf=['Dead:TargetDisease','Dead:Other','Withdrawal','Trial end'])).transform_filter(alt.FieldEqualPredicate(field='dummy', equal=False))
   
    ticks = base.mark_point(filled=True).encode(
    color=alt.value("black"),
    size=alt.value(25),
    shape=alt.value("circle"),#stroke
    opacity=alt.value(.8),
    tooltip=['Treatment_arm', 'Participant',  'days_from_treatment','days_from_randomization',
    'event_outcome', 'event_type']).transform_filter(alt.FieldEqualPredicate(field='event_type', equal='scan'))

    reference_line= alt.Chart(pd.DataFrame({'x':[0]})).mark_rule(color='black', size=1).encode(x='x')

    chart = (line + point + ticks + reference_line + line0).properties(
            width=650,
            height=850,title=title
            ).resolve_scale(color='independent')
    return chart

def plot_simple_timeline(df,date='dates',date_title='dates',colour = "Treatment_arm",palette = ["#2354A9","#4190B1","#5D5F60"],
                       shape='measurement',
                       tooltip=['Participant'],
                       order ='(datum.Treatment_arm != "nan" ? 1 : 2) * min(datum.dates)',
                       title="ARM A"):
    
    base = alt.Chart(df).transform_calculate(
    order=order
        ).encode(
        alt.X(f"{date}").title(date_title),
        alt.Y("Participant:N",sort = alt.SortField('order')
              )
            .axis(offset=0, ticks=False, minExtent=0, domain=False)
    )

    line = base.mark_line().encode(
        detail="Participant",
        color=alt.value("black"),
        opacity=alt.value(.5),
    )

    point = base.mark_point(filled=True).encode(alt.Color(colour).scale(range=palette),
        size=alt.value(100),
        opacity=alt.value(.8),
        shape = shape,
        tooltip=tooltip)
        
    chart = (line + point).properties(
                width=800,
                height=850,title=title
            )
    return chart