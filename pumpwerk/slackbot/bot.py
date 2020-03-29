from django.conf import settings

import slack


def get_slack_client():
    return slack.WebClient(token=settings.SLACK_API_TOKEN, ssl=True)


def generate_bill_result_blocks(bill):
    # text = ''
    # for user_bill in bill.userbill_set.all().order_by('user__username'):
    #     text += f"*{user_bill.user}* ({user_bill.attendance_days:.1f}): [{user_bill.credit:.2f} - {user_bill.food_sum:.2f} - {user_bill.invest_sum:.2f} - {user_bill.luxury_sum:.2f}] *{user_bill.total:.2f}*\n"
    result = [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Essensabrechnung: {bill.get_month()} {bill.year}*"
                    }
                },
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"Summe Anwesenheitstage: {bill.total_attendance_days:.2f}\nSumme Terra: {bill.total_terra:.2f}€\nSumme Supermarkt: {bill.total_supermarket:.2f}€\nSumme Invest: {bill.total_invest:.2f}€\nTagessatz (Terra): {bill.daily_rate:.2f} €({bill.terra_daily_rate:.2f}€)"
                        }
                    ]
                },
            ]
    fields = []
    fields.append({"type": "mrkdwn", "text":"_User (Anwesenheitstage)_"})
    fields.append({"type": "mrkdwn", "text":"_Summe (Kredit + Ausgaben - Essen - Invest - Luxus)_"})
    result.append({
        "type": "section",
        "fields": fields,
    })
    fields = []
    for user_bill in bill.userbill_set.all().order_by('user__username'):
        fields.append({"type": "mrkdwn", "text":f"*{user_bill.user}* ({user_bill.attendance_days:.1f}):"})
        fields.append({"type": "mrkdwn", "text":f"*{user_bill.total:.2f}* ({user_bill.credit:.2f} + {user_bill.expense_sum:.2f} - {user_bill.food_sum:.2f} - {user_bill.invest_sum:.2f} - {user_bill.luxury_sum:.2f})"})
        result.append({
            "type": "section",
            "fields": fields,
        })
        fields = []
    return result

def send_message_to_channel(channel, bill):
    # raise Exception(generate_bill_result_blocks(bill))
    client = get_slack_client()
    response = client.chat_postMessage(
        channel=channel,
        blocks=generate_bill_result_blocks(bill))
    return response['ok']