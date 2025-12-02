import { Routes } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { TransacoesComponent } from './transacoes/transacoes.component';
import { GastosFixosComponent } from './gastos-fixos/gastos-fixos.component';
import { LembretesComponent } from './lembretes/lembretes.component';
import { DicasComponent } from './dicas/dicas.component';
import { EntrarComponent } from './entrar/entrar.component';
import { CadastrarComponent } from './cadastrar/cadastrar.component';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
	{ path: '', component: HomeComponent },
	{ path: 'home', component: HomeComponent },
	{ path: 'dashboard', component: DashboardComponent, canActivate: [AuthGuard] },
	{ path: 'transacoes', component: TransacoesComponent, canActivate: [AuthGuard] },
	{ path: 'gastos-fixos', component: GastosFixosComponent, canActivate: [AuthGuard] },
	{ path: 'lembretes', component: LembretesComponent, canActivate: [AuthGuard] },
	{ path: 'dicas', component: DicasComponent, canActivate: [AuthGuard] },
	{ path: 'entrar', component: EntrarComponent },
	{ path: 'cadastrar', component: CadastrarComponent },
	{ path: '**', redirectTo: '' }
];
