from devsecscan.cli.main import main


def test_cli_outputs_repository_risk_summary_for_clean_repo(tmp_path, capsys):
    (tmp_path / "app.py").write_text("print('safe')\n")

    exit_code = main([str(tmp_path)])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "Repository Risk Summary" in output
    assert "Total Findings: 0" in output
    assert "Deployment Recommendation:\nSAFE" in output
