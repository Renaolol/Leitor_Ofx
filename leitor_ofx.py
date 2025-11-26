from ofxparse import OfxParser

with open("MAIZA.ofx",'r') as fileobj:
    ofx = OfxParser.parse(fileobj)

account = ofx.account
statement = account.statement
total_debitos = 0
for transaction in statement.transactions:
    if transaction.type == "debit":
        total_debitos += transaction.amount
        print(transaction.payee,
                transaction.type,
                transaction.date,
                transaction.amount,
                transaction.memo)

print(f"Total de débitos = R$ {total_debitos}")            