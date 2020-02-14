import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [data, setData] = useState({
    id: '',
    balance: 0,
    transactions: [],
  });

  const baseURL = 'http://localhost:5000';

  const fetchData = () => {
    fetch(`${baseURL}/chain`)
      .then(res => res.json())
      .then(res => {
        console.log(res)
        let transactions = res.chain
        .map(block => block.transactions)
        .flat();
        setData({...data, transactions });
      })
      .catch(err => console.log(err))
  };

  useEffect(() => {
    fetchData();
  }, []);

  function runningBalance() {

    fetch(`${baseURL}/chain`)
      .then(res => res.json())
      .then(res => {
        console.log(res)
        let transactions = res.chain
        .map(block => block.transactions)
        .flat();
        setData({...data, transactions });
        
        const moneyIn = transactions.filter(transaction => transaction.recipient === "0")
                        .reduce((bal, tran) => bal + tran.amount, 0)

        const moneyOut = transactions.filter(transaction => transaction.sender === '0')
                        .reduce((bal, tran) => bal + tran.amount, 0)
        
        const total = moneyIn - moneyOut;
        
        return total;
      })
      .catch(err => console.log(err))
  }

  const changeId = e => setData({ ...data, id: e.target.value })

  const handleClick = () => fetchData();

  return (
    <div className="App">
      <h1>Wallet</h1>
      {/* <input
        type="text"
        name="id"
        placeholder="Enter ID to search"
        value={data.sender}
        onChange={changeId}
      /> */}
      <button onClick={handleClick}>Update History</button>
      <h2>Current Balance:</h2>
      {runningBalance()}
      <h2>Account History:</h2>
      <>
        {data.transactions.map((transaction, index) => (
          <p>{transaction.sender} paid {transaction.recipient} {transaction.amount} coins</p>
        ))}
      </>
    </div>
  );
}

export default App;
