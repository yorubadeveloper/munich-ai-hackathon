from eval.metrics import compute_mean_f1, compute_per_label_f1, normalize_text, token_overlap_f1


def test_normalize_text():
    assert normalize_text("Hello World!") == "hello world"
    assert normalize_text(None) == ""
    assert normalize_text("  SPACES  and\tTabs ") == "spaces and tabs"
    assert normalize_text("Python, React, and Node.js") == "python react and nodejs"

def test_token_overlap_f1_exact():
    assert token_overlap_f1("Senior Engineer", "Senior Engineer") == 1.0
    assert token_overlap_f1("Python, React", "Python, React") == 1.0

def test_token_overlap_f1_partial():
    # Predicted: "python react nodejs" (3 tokens)
    # GT: "python react" (2 tokens)
    # Common: 2
    # Precision = 2/3, Recall = 2/2 = 1.0
    # F1 = 2 * (2/3 * 1) / (2/3 + 1) = 4/3 / 5/3 = 0.8
    score = token_overlap_f1("Python, React, Node.js", "Python, React")
    assert abs(score - 0.8) < 1e-5

def test_token_overlap_f1_zero():
    assert token_overlap_f1("Java", "Python") == 0.0

def test_token_overlap_f1_empty():
    assert token_overlap_f1("", "") == 1.0
    assert token_overlap_f1("Something", "") == 0.0
    assert token_overlap_f1(None, "Something") == 0.0
    assert token_overlap_f1(None, None) == 1.0

def test_compute_per_label_f1():
    predictions = {
        "company_name": "TechCorp",
        "job_title": "Engineer",
        "salary": "100k"
    }
    ground_truth = {
        "company_name": "TechCorp Inc",
        "job_title": "Software Engineer",
        "salary": "100k"
    }
    labels = ["company_name", "job_title", "salary", "remote_policy"]

    scores = compute_per_label_f1(predictions, ground_truth, labels)

    # company_name: "techcorp" vs "techcorp inc" -> F1 = 2*(1*0.5)/(1.5) = 2/3 ~ 0.666
    assert abs(scores["company_name"] - 0.666666) < 1e-4
    # job_title: "engineer" vs "software engineer" -> F1 = 2*(1*0.5)/(1.5) = 2/3 ~ 0.666
    assert abs(scores["job_title"] - 0.666666) < 1e-4
    # salary: exact match
    assert scores["salary"] == 1.0
    # remote_policy: both absent
    assert scores["remote_policy"] == 1.0

def test_compute_mean_f1():
    scores = {"a": 1.0, "b": 0.5, "c": 0.0}
    assert compute_mean_f1(scores) == 0.5
    assert compute_mean_f1({}) == 0.0
