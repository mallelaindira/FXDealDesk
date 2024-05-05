#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 18 17:41:55 2023

@author: indiramallela
"""

import pandas as pd
from datetime import datetime
import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QInputDialog, QMessageBox


class FXDealApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('FX Deal App')
        self.setGeometry(100, 100, 400, 200)

        self.buy_button = QPushButton('Buy', self)
        self.buy_button.setGeometry(50, 50, 100, 40)
        self.buy_button.clicked.connect(self.buy_dialog)

        self.sell_button = QPushButton('Sell', self)
        self.sell_button.setGeometry(250, 50, 100, 40)
        self.sell_button.clicked.connect(self.sell_dialog)

    def buy_dialog(self):
        amount, ok = QInputDialog.getDouble(self, 'Buy FX Deal', 'Enter the amount in USD:')
        if ok:
            rate, ok = self.rate_dialog()
            if ok:
                self.execute_deal('buy', amount, rate)

    def sell_dialog(self):
        amount, ok = QInputDialog.getDouble(self, 'Sell FX Deal', 'Enter the amount in USD:')
        if ok:
            rate, ok = self.rate_dialog()
            if ok:
                self.execute_deal('sell', amount, rate)

    def rate_dialog(self):
        rate, ok = QInputDialog.getDouble(self, 'Enter Rate', 'Enter the rate:')
        return rate, ok

    def execute_deal(self, deal_type, amount_usd, rate):
        # Load the Excel file
        file_path = 'fx_desk.xlsx'
        df_rate = pd.read_excel(file_path, sheet_name='rate')
        df_balances = pd.read_excel(file_path, sheet_name='balances')

        # Calculate the date
        current_date = datetime.now().strftime('%Y-%m-%d')

        # Calculate amount_inr
        amount_inr = amount_usd * rate

        # Check if sufficient balance is available
        current_balance_usd = df_balances['balance_usd'].iloc[-1]
        if (deal_type == 'sell' and amount_usd > current_balance_usd) or (
                deal_type == 'buy' and amount_inr > df_balances['balance_inr'].iloc[-1]):
            QMessageBox.critical(self, 'Insufficient Funds', 'Insufficient funds. Deal cannot be executed.')
        else:
            # Update balances sheet
            new_balance_usd = current_balance_usd - amount_usd if deal_type == 'sell' else current_balance_usd + amount_usd
            new_balance_inr = df_balances['balance_inr'].iloc[-1] + amount_inr if deal_type == 'sell' else df_balances[
                                                                                                                  'balance_inr'].iloc[
                                                                                                              -1] - amount_inr

            # Create a new row for the transaction
            new_row = {
                'date': current_date,
                'buy_sell': deal_type,
                'rate': rate,
                'amount_usd': amount_usd,
                'amount_inr': amount_inr,
                'balance_usd': new_balance_usd,
                'balance_inr': new_balance_inr
            }

            df_balances = df_balances._append(new_row, ignore_index=True)

            # Save the updated balances sheet back to the Excel file
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
                df_balances.to_excel(writer, sheet_name='balances', index=False)

            QMessageBox.information(self, 'Deal Executed', 'Deal executed successfully and balances updated.')
            fig, ax1 = plt.subplots()

            # Plot 'balance_usd' on the primary axis (ax1)
            ax1.plot(df_balances['date'], df_balances['balance_usd'], label='Balance (USD)', color='b', marker='*')
            ax1.set_xlabel('Date')
            ax1.set_ylabel('Balance (USD)', color='b')
            ax1.tick_params(axis='y', labelcolor='b')

            # Create a secondary axis for 'amount_inr'
            ax2 = ax1.twinx()
            ax2.plot(df_balances['date'], df_balances['balance_inr'], label='Balance (INR)', color='r', marker='o')
            ax2.set_ylabel('Balance (INR)', color='r')
            ax2.tick_params(axis='y', labelcolor='r')

            # Display legends
            fig.tight_layout()
            plt.legend(loc='best')
            plt.title('Balance Over Time')
            plt.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    fx_app = FXDealApp()
    fx_app.show()
    sys.exit(app.exec_())