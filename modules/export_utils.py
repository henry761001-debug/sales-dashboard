"""
匯出與圖表生成模組
負責生成 Excel 檔案、圖表圖片等
"""

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from typing import Optional, Tuple
from io import BytesIO


class ExcelExporter:
    """Excel 匯出器"""
    
    @staticmethod
    def export_dataframe(
        df: pd.DataFrame,
        file_path: str,
        sheet_name: str = "Data"
    ) -> Tuple[bool, str]:
        """
        匯出 DataFrame 為 Excel
        """
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return True, f"成功匯出到 {file_path}"
        
        except Exception as e:
            return False, f"匯出失敗: {str(e)}"
    
    @staticmethod
    def export_multiple_sheets(
        data_dict: dict,
        file_path: str
    ) -> Tuple[bool, str]:
        """
        匯出多個 Sheet
        data_dict: {sheet_name: dataframe}
        """
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                for sheet_name, df in data_dict.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return True, f"成功匯出到 {file_path}"
        
        except Exception as e:
            return False, f"匯出失敗: {str(e)}"
    
    @staticmethod
    def get_excel_bytes(
        df: pd.DataFrame,
        sheet_name: str = "Data"
    ) -> Optional[bytes]:
        """
        獲取 Excel 檔案的位元組內容
        """
        try:
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            buffer.seek(0)
            return buffer.getvalue()
        
        except Exception as e:
            print(f"生成 Excel 失敗: {str(e)}")
            return None


class ChartGenerator:
    """圖表生成器"""
    
    @staticmethod
    def create_sales_trend_chart(
        df: pd.DataFrame,
        title: str = "銷售趨勢"
    ) -> go.Figure:
        """
        建立銷售趨勢圖表
        """
        if df.empty:
            return go.Figure().add_annotation(text="無資料")
        
        # 按日期分組
        daily_sales = df.groupby(df['日期'].dt.date)['銷售金額'].sum().reset_index()
        daily_sales.columns = ['日期', '銷售金額']
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=daily_sales['日期'],
            y=daily_sales['銷售金額'],
            mode='lines+markers',
            name='銷售金額',
            line=dict(color='#003366', width=3),
            marker=dict(size=8, color='#FF6B35'),
            fill='tozeroy',
            fillcolor='rgba(0, 51, 102, 0.1)'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='日期',
            yaxis_title='銷售金額 (NT$)',
            hovermode='x unified',
            template='plotly_white',
            height=400
        )
        
        return fig
    
    @staticmethod
    def create_top_products_chart(
        df: pd.DataFrame,
        top_n: int = 10,
        sort_by: str = 'sales',
        title: str = "排名前 10 產品"
    ) -> go.Figure:
        """
        建立產品排行圖表
        """
        if df.empty:
            return go.Figure().add_annotation(text="無資料")
        
        if sort_by == 'sales':
            top_data = df.nlargest(top_n, '銷售金額')
            y_col = '銷售金額'
            y_title = '銷售金額 (NT$)'
        else:
            top_data = df.nlargest(top_n, '數量')
            y_col = '數量'
            y_title = '銷售數量'
        
        # 建立產品標籤
        top_data['標籤'] = top_data['產品名稱'] + ' (' + top_data['零件號'] + ')'
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=top_data['標籤'],
            x=top_data[y_col],
            orientation='h',
            marker=dict(
                color=top_data[y_col],
                colorscale='Blues',
                showscale=True
            ),
            text=top_data[y_col].apply(lambda x: f'{x:,.0f}'),
            textposition='outside'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title=y_title,
            yaxis_title='產品',
            height=500,
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_group_comparison_chart(
        df: pd.DataFrame,
        title: str = "集團銷售比較"
    ) -> go.Figure:
        """
        建立集團銷售比較圖表
        """
        if df.empty:
            return go.Figure().add_annotation(text="無資料")
        
        group_sales = df.groupby('Group_Name')['銷售金額'].sum().sort_values(ascending=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=group_sales.index,
            x=group_sales.values,
            orientation='h',
            marker=dict(
                color=group_sales.values,
                colorscale='Viridis'
            ),
            text=group_sales.values.apply(lambda x: f'NT${x:,.0f}'),
            textposition='outside'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='銷售金額 (NT$)',
            yaxis_title='集團',
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_dlr_comparison_chart(
        df: pd.DataFrame,
        title: str = "經銷商銷售比較"
    ) -> go.Figure:
        """
        建立經銷商銷售比較圖表
        """
        if df.empty:
            return go.Figure().add_annotation(text="無資料")
        
        dlr_sales = df.groupby('DLR_Name')['銷售金額'].sum().sort_values(ascending=True)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=dlr_sales.index,
            x=dlr_sales.values,
            orientation='h',
            marker=dict(
                color=dlr_sales.values,
                colorscale='Blues'
            ),
            text=dlr_sales.values.apply(lambda x: f'NT${x:,.0f}'),
            textposition='outside'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='銷售金額 (NT$)',
            yaxis_title='經銷商',
            height=500,
            template='plotly_white',
            showlegend=False
        )
        
        return fig
    
    @staticmethod
    def create_kpi_gauge_chart(
        value: float,
        max_value: float = 100,
        title: str = "KPI 進度"
    ) -> go.Figure:
        """
        建立 KPI 進度表
        """
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            title={'text': title},
            delta={'reference': max_value},
            gauge={
                'axis': {'range': [0, max_value]},
                'bar': {'color': '#003366'},
                'steps': [
                    {'range': [0, max_value * 0.5], 'color': '#FADBD8'},
                    {'range': [max_value * 0.5, max_value * 0.8], 'color': '#FCF3CF'},
                    {'range': [max_value * 0.8, max_value], 'color': '#D5F4E6'}
                ],
                'threshold': {
                    'line': {'color': 'red', 'width': 4},
                    'thickness': 0.75,
                    'value': max_value
                }
            }
        ))
        
        fig.update_layout(height=400, template='plotly_white')
        return fig
    
    @staticmethod
    def create_monthly_comparison_chart(
        df: pd.DataFrame,
        title: str = "月度銷售對比"
    ) -> go.Figure:
        """
        建立月度銷售對比圖表
        """
        if df.empty:
            return go.Figure().add_annotation(text="無資料")
        
        df['月份'] = df['日期'].dt.to_period('M')
        monthly_sales = df.groupby('月份')['銷售金額'].sum().reset_index()
        monthly_sales['月份'] = monthly_sales['月份'].astype(str)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=monthly_sales['月份'],
            y=monthly_sales['銷售金額'],
            marker=dict(color='#003366'),
            text=monthly_sales['銷售金額'].apply(lambda x: f'NT${x:,.0f}'),
            textposition='outside'
        ))
        
        fig.update_layout(
            title=title,
            xaxis_title='月份',
            yaxis_title='銷售金額 (NT$)',
            height=400,
            template='plotly_white',
            showlegend=False
        )
        
        return fig


class ImageExporter:
    """圖片匯出器"""
    
    @staticmethod
    def export_figure_as_image(
        fig: go.Figure,
        file_path: str,
        format: str = 'png'
    ) -> Tuple[bool, str]:
        """
        匯出 Plotly 圖表為圖片
        """
        try:
            fig.write_image(file_path, format=format, width=1200, height=600)
            return True, f"成功匯出圖表到 {file_path}"
        
        except Exception as e:
            return False, f"匯出圖表失敗: {str(e)}"
    
    @staticmethod
    def export_figure_as_html(
        fig: go.Figure,
        file_path: str
    ) -> Tuple[bool, str]:
        """
        匯出 Plotly 圖表為 HTML
        """
        try:
            fig.write_html(file_path)
            return True, f"成功匯出圖表到 {file_path}"
        
        except Exception as e:
            return False, f"匯出圖表失敗: {str(e)}"


class ReportGenerator:
    """報告生成器"""
    
    @staticmethod
    def generate_summary_report(
        boutique_df: pd.DataFrame,
        beauty_df: pd.DataFrame,
        target_df: pd.DataFrame,
        period: str = "YTD"
    ) -> str:
        """
        生成摘要報告文本
        """
        report = f"# 銷售報告 ({period})\n\n"
        report += f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # 精品銷售統計
        if not boutique_df.empty:
            total_boutique = boutique_df['銷售金額'].sum()
            boutique_jobs = boutique_df['工單號'].nunique()
            report += f"## 精品銷售\n"
            report += f"- 總銷售額: NT${total_boutique:,.0f}\n"
            report += f"- 工單數: {boutique_jobs}\n"
            report += f"- 平均工單金額: NT${total_boutique/boutique_jobs:,.0f}\n\n"
        
        # 美容銷售統計
        if not beauty_df.empty:
            total_beauty = beauty_df['銷售金額'].sum()
            beauty_jobs = beauty_df['工作單號'].nunique()
            report += f"## 美容銷售\n"
            report += f"- 總銷售額: NT${total_beauty:,.0f}\n"
            report += f"- 工作單數: {beauty_jobs}\n"
            report += f"- 平均工作單金額: NT${total_beauty/beauty_jobs:,.0f}\n\n"
        
        # 集團分析
        if not boutique_df.empty:
            report += f"## 集團銷售排名\n"
            group_sales = boutique_df.groupby('Group_Name')['銷售金額'].sum().sort_values(ascending=False)
            for i, (group, sales) in enumerate(group_sales.head(5).items(), 1):
                report += f"{i}. {group}: NT${sales:,.0f}\n"
            report += "\n"
        
        return report
