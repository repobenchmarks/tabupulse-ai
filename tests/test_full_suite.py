from fastapi.testclient import TestClient
from backend.app.main import app

def test_full_application_suite():
    client = TestClient(app)

    # 1. Health
    res_health = client.get('/api/health')
    assert res_health.status_code == 200
    assert res_health.json()['status'] == 'healthy'
    print('✔ Health endpoint verified')

    # 2. Sample datasets
    res_samples = client.get('/api/sample-datasets')
    assert res_samples.status_code == 200
    assert len(res_samples.json()['datasets']) == 2
    print('✔ Sample datasets endpoint verified (2 datasets)')

    # 3. Ecommerce Churn Prediction
    res_ecom = client.post('/api/predict', json={'dataset_id': 'ecommerce_churn'})
    assert res_ecom.status_code == 200
    ecom_data = res_ecom.json()
    assert ecom_data['target_column'] == 'churned'
    assert ecom_data['revenue_playbook']['high_risk_count'] > 0
    print('✔ E-Commerce Churn prediction verified (Zero-shot TabPFN)')

    # 4. Freelance Cashflow Prediction
    res_free = client.post('/api/predict', json={'dataset_id': 'freelance_cashflow'})
    assert res_free.status_code == 200
    free_data = res_free.json()
    assert free_data['target_column'] == 'late_payment'
    assert free_data['revenue_playbook']['delayed_invoices_count'] > 0
    print('✔ Freelance Cashflow prediction verified')

    # 5. MCP Info
    res_mcp = client.get('/api/mcp-info')
    assert res_mcp.status_code == 200
    assert len(res_mcp.json()['tools']) == 3
    print('✔ Model Context Protocol (MCP) server tools verified')

    # 6. Static Root HTML
    res_root = client.get('/')
    assert res_root.status_code == 200
    assert len(res_root.text) > 100
    print('✔ Static frontend production root serving verified')

    print('\n🎉 All test suites passed successfully!')

if __name__ == '__main__':
    test_full_application_suite()
