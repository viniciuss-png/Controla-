import { Routes } from '@angular/router';
import { HomeComponent } from './components/home/home.component';
import { EntrarComponent } from './components/entrar/entrar.component';
import { CadastrarComponent } from './components/cadastrar/cadastrar.component';
import { DashboardComponent } from './components/dashboard/dashboard.component';
import { TransacoesComponent } from './components/transacoes/transacoes.component';
import { GastosFixosComponent } from './components/gastos-fixos/gastos-fixos.component';
import { LembretesComponent } from './components/lembretes/lembretes.component';
import { DicasComponent } from './components/dicas/dicas.component';
import { transacoesResolver } from './services/transacoes.resolver';
import { lembretesResolver } from './services/lembretes.resolver';
import { dashboardResolver } from './services/dashboard.resolver';

export const routes: Routes = [
	{ path: '', component: HomeComponent },
	{ path: 'entrar', component: EntrarComponent },
	{ path: 'cadastrar', component: CadastrarComponent },
	{ path: 'dashboard', component: DashboardComponent, resolve: { dashboard: dashboardResolver } },
	{ path: 'transacoes', component: TransacoesComponent, resolve: { transacoes: transacoesResolver } },
	{ path: 'gastos-fixos', component: GastosFixosComponent },
	{ path: 'lembretes', component: LembretesComponent, resolve: { lembretes: lembretesResolver } },
	{ path: 'dicas', component: DicasComponent }
];
