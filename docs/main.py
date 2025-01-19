import yfinance as yf
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Tickers for the largest companies in each S&P 500 sector
tickers = ["GOOG", "AMZN", "WMT", "XOM", "BRK-B", "LLY", "GE", "MSFT", "LIN", "PLD", "NEE"]
index_ticker = "^GSPC"  # S&P 500 index ticker

try:
    # Get data from 2020 to present
    data = yf.download(tickers + [index_ticker], start="2020-01-01", end=datetime.now().strftime('%Y-%m-%d'), interval="1d")
    
    # Get company names
    company_names = {}
    for ticker in tickers:
        try:
            company = yf.Ticker(ticker)
            company_names[ticker] = company.info.get('longName', ticker)
        except:
            company_names[ticker] = ticker
    
    # Check if data is empty
    if data.empty:
        raise ValueError("No data was fetched from Yahoo Finance")
    
    # Check available columns and use Close if Adj Close is not available
    price_column = 'Adj Close' if 'Adj Close' in data.columns else 'Close'
    if price_column not in data.columns:
        raise ValueError("Neither 'Adj Close' nor 'Close' columns are available in the data")
    
    # Extract the price data
    price_data = data[price_column]

    # Create a figure with subplots in a 3xN layout
    current_year = datetime.now().year
    num_years = current_year - 2020 + 1
    
    # Calculate rows and columns needed
    num_rows = 3
    num_cols = (num_years + 2 + num_rows - 1) // num_rows  # Ceiling division to ensure enough columns
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(8*num_cols, 5*num_rows))  # 3xN layout
    axes = axes.flatten()  # Flatten the 2D array of axes to make it easier to iterate
    
    for idx, year in enumerate(range(2020, current_year + 1)):
        ax = axes[idx]
        if idx < num_years:  # For all year plots
            # Filter data for the specific year
            year_start = f"{year}-01-01"
            year_end = f"{year}-12-31" if year != current_year else datetime.now().strftime('%Y-%m-%d')
            year_data = price_data.loc[year_start:year_end]
            
            # Calculate the daily returns for the year
            daily_returns = year_data.pct_change()
            
            # Calculate the average return for the year
            average_returns = daily_returns.mean() * 252  # Annualized return
            
            # Separate the S&P 500 index return from the company returns
            average_returns = average_returns.dropna()
            sector_returns = average_returns.drop(index_ticker)
            snp_return = average_returns[index_ticker]
            
            # Convert returns to percentages
            sector_returns = sector_returns * 100
            snp_return = snp_return * 100
            
            # Calculate the average of sector leaders
            sector_leaders_avg = sector_returns.mean()
            
            # Create the subplot
            ax.bar(sector_returns.index, sector_returns, color="blue", alpha=0.7, label="Sector Leaders")
            ax.axhline(y=snp_return, color="red", linestyle="--", label=f"S&P 500 ({snp_return:.1f}%)")
            ax.axhline(y=sector_leaders_avg, color="green", linestyle="--", label=f"Sector Leaders Avg ({sector_leaders_avg:.1f}%)")
            ax.set_xlabel("Company Tickers")
            ax.set_ylabel("Average Annual Return (%)")
            ax.set_title(f"Average Annual Return of Sector Leaders vs S&P 500 ({year})")
            ax.legend()
            ax.tick_params(axis='x', rotation=45)
            ax.grid(axis='y', linestyle='--', alpha=0.3)

    # Add cumulative return plot in the next position
    ax = axes[num_years]
    # Calculate cumulative returns from 2020 to present
    portfolio_returns = []
    snp_returns = []
    years = []
    
    for year in range(2020, current_year + 1):
        year_start = f"{year}-01-01"
        year_end = f"{year}-12-31" if year != current_year else datetime.now().strftime('%Y-%m-%d')
        year_data = price_data.loc[year_start:year_end]
        daily_returns = year_data.pct_change()
        average_returns = daily_returns.mean() * 252 * 100  # Annualized return in percentage
        
        # Calculate portfolio average (excluding S&P 500)
        portfolio_return = average_returns.drop(index_ticker).mean()
        snp_return = average_returns[index_ticker]
        
        portfolio_returns.append(portfolio_return)
        snp_returns.append(snp_return)
        years.append(year)
    
    # Plot the comparison
    ax.plot(years, portfolio_returns, marker='o', label='Portfolio Average', color='blue', linewidth=2)
    ax.plot(years, snp_returns, marker='o', label='S&P 500', color='red', linewidth=2)
    
    ax.set_xlabel('Year')
    ax.set_ylabel('Annual Return (%)')
    ax.set_title('Portfolio vs S&P 500 Performance Over Time')
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Add value labels on the points
    for i, (p_ret, s_ret) in enumerate(zip(portfolio_returns, snp_returns)):
        ax.annotate(f'{p_ret:.1f}%', (years[i], p_ret), textcoords="offset points", xytext=(0,10), ha='center')
        ax.annotate(f'{s_ret:.1f}%', (years[i], s_ret), textcoords="offset points", xytext=(0,-15), ha='center')

    # Add table in the last position
    ax = axes[num_years + 1]
    ax.axis('off')  # Turn off axis
    
    # Create data for the table
    table_data = []
    
    # Get the actual date range for the current year
    year_start = f"{current_year}-01-01"
    year_end = datetime.now().strftime('%Y-%m-%d')
    date_range = f"{year_start} to {year_end}"
    
    headers = ['Ticker', 'Company Name', f'Return ({date_range})']
    
    # Calculate returns for the current year
    year_data = price_data.loc[year_start:year_end]
    daily_returns = year_data.pct_change()
    average_returns = (daily_returns.mean() * 252 * 100).round(2)  # Annualized return in percentage
    
    # Create table data
    for ticker in tickers:
        table_data.append([
            ticker,
            company_names[ticker],
            f"{average_returns[ticker]:.2f}%"
        ])
    
    # Add S&P 500 row
    table_data.append([
        index_ticker,
        "S&P 500 Index",
        f"{average_returns[index_ticker]:.2f}%"
    ])
    
    # Create table
    table = ax.table(
        cellText=table_data,
        colLabels=headers,
        loc='center',
        cellLoc='center',
        colColours=['#f2f2f2']*3,
        cellColours=[['#ffffff']*3 for _ in range(len(table_data))],
    )
    
    # Style the table
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.5)
    
    # Set title
    ax.set_title(f"Performance Summary {current_year}", pad=20)

    # Hide any empty subplots
    for idx in range(num_years + 2, num_rows * num_cols):
        axes[idx].set_visible(False)

    plt.tight_layout()
    plt.show()

except Exception as e:
    print(f"An error occurred: {str(e)}")
    # Print additional debugging information
    if 'data' in locals():
        print("\nAvailable columns in data:")
        print(data.columns)
