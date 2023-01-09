def styling(fig, headline, subhead, xaxes_title, yaxes_title, figHeight, marginTop, showLegend):
    
    textcolor = 'rgba(24,24,24,1)'
    fontFamily = 'Manrope, Sohne, Inter, Arial'
    fontHeadline = 'Test Söhne, Sohne, Manrope, Inter, Arial'
    axeslinecolor = 'rgba(24,24,24,1)'
    gridcolor = 'rgba(245,245,245,1)'
    
    fig.update_layout(width = None, height = figHeight, plot_bgcolor='rgba(255,255,255,0)', paper_bgcolor='rgba(255,255,255,0)')
    fig['layout'].update(margin=dict(l=0,r=0,b=0,t=marginTop))
    fig.update_layout(font_family=fontFamily, font_color=textcolor, font_size=8)
    
    fig.update_layout(title=f'<span style="font-size: 18px; font-weight:600">{headline}</span><br><span style="font-family: {fontFamily}; font-size: 11px">{subhead}</span>')
    fig.update_layout(title=dict(font=dict(family=fontHeadline, size=16, color='#181818'))) 
    fig.update_layout(title={'y':0.95,'x':0,'xanchor': 'left','yanchor': 'top'})
    
    fig.update_xaxes(title=xaxes_title)
    fig.update_xaxes(showline=True, linewidth=1, linecolor=axeslinecolor, mirror=False, tickfont=dict(size=6), tickangle=270)
    fig.update_xaxes(showgrid=False, gridwidth=1, gridcolor=gridcolor)

    fig.update_yaxes(title=yaxes_title)
    fig.update_yaxes(showline=False, linewidth=1, linecolor=axeslinecolor, mirror=False, tickfont=dict(size=6), ticklabelposition="inside top")
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor=gridcolor)
        
    fig.update_layout(showlegend=showLegend, legend=dict(orientation='h', yanchor="bottom", y=1, xanchor="right", x=1, font = dict(size = 10, color = "#181818")))
        
######################################################

def mobileStyling(figMOBILE, headline, subheadMobile, marginTop):
    
    figMOBILE.update_layout(title={'y':0.9})
    figMOBILE['layout'].update(margin=dict(t=marginTop+50))
    figMOBILE.update_layout(legend=dict(orientation='v'))