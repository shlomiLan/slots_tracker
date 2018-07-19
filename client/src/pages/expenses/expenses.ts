import { Component } from '@angular/core';
import { NavController, ModalController, NavParams, ModalOptions, ToastController } from 'ionic-angular';
import { ApiServiceProvider } from '../../providers/api-service/api-service'
import 'rxjs/add/operator/do'


@Component({
  selector: 'page-expenses',
  templateUrl: 'expenses.html'
})

export class ExpensesPage {
  expenses: any;
  methods: any;

  constructor(public navCtrl: NavController, public navParams: NavParams, public modalCtrl: ModalController,
              private api: ApiServiceProvider, public toastCtrl: ToastController) {

    // Inittialize data
    this.getExpenses();
    this.getPayMethods();
  }

  // Logic for creating or updating expense
  createOrUpdateExpense(data = undefined) {
    if (!data){
      // TODO: Remove this section to return an empty structure
      data = {amount: undefined, descreption: ''};
      // pay_method: '', timestamp: ''}
    }

    const myModalOptions: ModalOptions = {
      enableBackdropDismiss: false
    }

    let modal = this.modalCtrl.create('ExpenseModalPage', {data: data}, myModalOptions);
      modal.onDidDismiss(data => {
        if (data){
          this.api.creatOrUpdateExpense(data).subscribe(res => {this.getExpenses()});
        }
      });

      modal.present();
  }


  // Logic for creating or updating expense
  createOrUpdatePayMethod(data = undefined) {
    if (!data){
      // TODO: Remove this section to return an empty structure
      data = {name: undefined};
    }

    const myModalOptions: ModalOptions = {
      enableBackdropDismiss: false
    }

    let modal = this.modalCtrl.create('PayMethodModalPage', {data: data}, myModalOptions);
      modal.onDidDismiss(data => {
        if (data){
          this.api.createOrUpdatePayMethod(data).subscribe(res => {this.getPayMethods()}, err =>{
              const toast = this.toastCtrl.create({
                message: err.error,
                duration: 3000,
                position: 'top'
              });
              toast.present();
            });
        }
      });

      modal.present();
  }

  getExpenses() {
    this.api.getExpenses().subscribe(response => this.expenses = response);
  }

  getPayMethods() {
    this.api.getPayMethods().subscribe(response => this.methods = response);
  }
}
