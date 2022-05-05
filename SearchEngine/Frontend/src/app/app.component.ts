import {Component, OnInit} from '@angular/core';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent implements OnInit{
  title = 'Frontend';

  results: any;
  userQuery = 'computer';
  isLoading = false;

  constructor(private http: HttpClient) {

  }


  ngOnInit(): void {
  }

  makeQuery() {
    this.isLoading = true;
    this.http.get('http://127.0.0.1:5000/search?query=' + encodeURIComponent(this.userQuery)).subscribe(
      (data) => {
        this.results = data
        this.isLoading = false;
      },
      (error) => {
        this.isLoading = false;
        this.results = [["error", "error"]]
      }
    )
  }
}
